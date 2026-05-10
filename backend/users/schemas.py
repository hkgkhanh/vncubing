from pydantic import BaseModel
from datetime import date

class UserPublic(BaseModel):
    id: str
    wca_id: str | None = None
    email: str
    name: str

    class Config:
        from_attributes = True

class UserFull(UserPublic):
    gender: str
    dob: date