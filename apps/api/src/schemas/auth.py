import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    account_type: str  # "personal" or "company"
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    account_type: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    account_type: str
    company_name: Optional[str] = None

    class Config:
        from_attributes = True