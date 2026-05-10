from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from .dependencies import generate_token, get_password_hash, verify_password, get_user_by_email, get_user_by_wca_id, get_current_user
from .schemas import LoginRequest, EmailPasswordSignupRequest
from users.schemas import UserPublic
from users.models import User
from db.dependencies import get_db
from sqlalchemy.orm import Session
import uuid
from urllib.parse import urlencode
import urllib.parse
import json

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
API_VERSION = os.getenv("API_VERSION")
API_PREFIX_WITH_VERSION = f"/api/v{API_VERSION}"
WCA_APP_ID = os.getenv("WCA_APP_ID")
WCA_SECRET = os.getenv("WCA_SECRET")

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post('/login')
def login(request_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, request_data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if verify_password(request_data.password, user.hashed_password):
        token = generate_token(request_data.email)
        return {
            'token': token
        }
    else:
        raise HTTPException(status_code=401, detail="Wrong email or password")
    

@router.post('/signup', response_model=UserPublic)
def signup(request_data: EmailPasswordSignupRequest, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=request_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_password = get_password_hash(request_data.password)
    from datetime import datetime, timezone
    now_timestamp = datetime.now(timezone.utc)
    db_user = User(
        id=uuid.uuid4().hex,
        email=request_data.email,
        hashed_password=hashed_password,
        name=request_data.name,
        gender=request_data.gender,
        dob=request_data.dob,
        created_at=now_timestamp
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user




@router.get('/oauth/wca/login')
def wca_login():
    params = {
        "client_id": WCA_APP_ID,
        "redirect_uri": f"{BACKEND_URL}{API_PREFIX_WITH_VERSION}/auth/oauth/wca/callback",
        "response_type": "code",
        "scope": "public dob email openid profile",
    }

    redirect_to = (
        "https://www.worldcubeassociation.org/oauth/authorize?"
        + urlencode(params)
    )

    return RedirectResponse(url=redirect_to)

@router.get("/oauth/wca/callback")
def wca_callback(code: str, db: Session = Depends(get_db)):
    data = urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "client_id": WCA_APP_ID,
        "client_secret": WCA_SECRET,
        "redirect_uri": f"{BACKEND_URL}{API_PREFIX_WITH_VERSION}/auth/oauth/wca/callback"
    }).encode()

    request = urllib.request.Request("https://www.worldcubeassociation.org/oauth/token",
        data=data,
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        response_data = response.read()

    token_data = json.loads(response_data)

    # now, get person info to update to vncubing db
    me_request = urllib.request.Request("https://www.worldcubeassociation.org/api/v0/me",
        headers={
            "Authorization": f"Bearer {token_data['access_token']}"
        },
        method="GET"
    )

    with urllib.request.urlopen(me_request) as me_response:
        me_response_data = me_response.read()

    me_data = json.loads(me_response_data)
    wca_me = me_data["me"]

    existing_user = get_user_by_wca_id(db, wca_id=me_data['me']['wca_id'])
    if existing_user:
        existing_user.name = me_data['me']['name']
        existing_user.gender = me_data['me']['gender']
        existing_user.dob = me_data['me']['dob']
        existing_user.email = me_data['me']['email']

        db.commit()
        db.refresh(existing_user)

        user = existing_user
    else:
        from datetime import datetime, timezone
        now_timestamp = datetime.now(timezone.utc)
        user = User(
            id=str(uuid.uuid4()),
            email=me_data['me']['email'],
            name=me_data['me']['name'],
            wca_id=me_data['me']['wca_id'],
            gender=me_data['me']['gender'],
            dob=me_data['me']['dob'],
            created_at=now_timestamp
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    token = generate_token(me_data['me']['email'])
    return {
        'token': token
    }

@router.get("/oauth/wca/link")
def link_existing_account_to_wca(current_user: User = Depends(get_current_user)):
    params = {
        "client_id": WCA_APP_ID,
        "redirect_uri": f"{BACKEND_URL}{API_PREFIX_WITH_VERSION}/auth/oauth/wca/link/callback",
        "response_type": "code",
        "scope": "public dob email openid profile",
        "state": current_user.id
    }

    redirect_to = (
        "https://www.worldcubeassociation.org/oauth/authorize?"
        + urlencode(params)
    )

    return RedirectResponse(redirect_to)

@router.get("/oauth/wca/link/callback")
def wca_link_callback(code: str, state: str, db: Session = Depends(get_db)):
    """
    state = current_user.id
    """
    current_user = db.query(User).filter(User.id == state).first()

    if current_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    #
    # exchange authorization code -> access token
    #
    token_request_data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "client_id": WCA_APP_ID,
        "client_secret": WCA_SECRET,
        "code": code,
        "redirect_uri": f"{BACKEND_URL}{API_PREFIX_WITH_VERSION}/auth/oauth/wca/link/callback"
    }).encode()

    token_request = urllib.request.Request(
        "https://www.worldcubeassociation.org/oauth/token",
        data=token_request_data,
        method="POST"
    )

    with urllib.request.urlopen(token_request) as token_response:
        token_response_data = token_response.read()

    token_data = json.loads(token_response_data)

    #
    # get WCA user info
    #
    me_request = urllib.request.Request(
        "https://www.worldcubeassociation.org/api/v0/me",
        headers={
            "Authorization": f"Bearer {token_data['access_token']}"
        },
        method="GET"
    )

    with urllib.request.urlopen(me_request) as me_response:
        me_response_data = me_response.read()

    me_data = json.loads(me_response_data)

    wca_me = me_data["me"]

    wca_name = wca_me["name"]
    wca_email = wca_me["email"]
    wca_id = wca_me["wca_id"]
    wca_gender=wca_me['gender']
    wca_dob=wca_me['dob']

    #
    # check if wca_id already linked to another account
    #
    existing_wca_user = (
        db.query(User)
        .filter(User.wca_id == wca_id)
        .first()
    )

    if (
        existing_wca_user is not None
        and existing_wca_user.id != current_user.id
    ):
        raise HTTPException(
            status_code=409,
            detail="WCA account already linked to another account"
        )

    #
    # check if WCA email already belongs to another account
    #
    existing_email_user = (
        db.query(User)
        .filter(User.email == wca_email)
        .first()
    )

    if (
        existing_email_user is not None
        and existing_email_user.id != current_user.id
    ):
        raise HTTPException(
            status_code=409,
            detail="WCA email already belongs to another account"
        )

    #
    # link account
    #
    current_user.email = wca_email
    current_user.name = wca_name
    current_user.wca_id = wca_id
    current_user.gender = wca_gender
    current_user.dob = wca_dob

    db.commit()
    db.refresh(current_user)

    return {
        "message": "WCA account linked successfully",
        "user": UserPublic.model_validate(current_user)
    }