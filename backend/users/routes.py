from fastapi import APIRouter, Depends
from auth.dependencies import get_current_user
from .schemas import UserFull
from .models import User

router = APIRouter()

@router.get("/me", response_model=UserFull)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user