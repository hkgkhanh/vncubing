from typing import Union, Any
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from users.models import User
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
import os
import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db.dependencies import get_db

load_dotenv()

ENCRYPT_ALGORITHM = os.getenv("ENCRYPT_ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
KEY_EXPIRE = 60 * 60 * 24 * 3  # Expired after 3 days

reusable_oauth2 = HTTPBearer(scheme_name='Authorization')
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def generate_token(email: Union[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=KEY_EXPIRE)
    to_encode = {
        "exp": expire, "email": email
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ENCRYPT_ALGORITHM)
    return encoded_jwt



def validate_token(credentials: HTTPAuthorizationCredentials) -> str:
    """
        Return the email of the token
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ENCRYPT_ALGORITHM])
        exp_timestamp = payload.get("exp")

        if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.now():
            raise HTTPException(status_code=403, detail="Token expired")

        return payload.get("email")

    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
    

def get_user_by_id(db: Session, id: str):
    return db.query(User).filter(User.id == id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_wca_id(db: Session, wca_id: str):
    return db.query(User).filter(User.wca_id == wca_id).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_email = validate_token(credentials)

    except:
        raise credentials_exception

    user = get_user_by_email(db, email=token_email)

    if user is None:
        raise credentials_exception

    return user