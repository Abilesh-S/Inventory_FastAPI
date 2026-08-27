from pydantic import BaseModel, EmailStr
from app.models.user import RoleEnum

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: RoleEnum
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"