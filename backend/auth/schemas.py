from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class EmailPasswordSignupRequest(BaseModel):
    name: str
    email: str
    password: str
    gender: str
    dob: str


class UserResponse(BaseModel):
    id: str
    email: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    id: str | None = None