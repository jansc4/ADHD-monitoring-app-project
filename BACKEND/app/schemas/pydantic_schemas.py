from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole        # 🔥 TO BYŁ BRAKUJĄCY ELEMENT


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    role: UserRole        # (opcjonalnie, ale polecam)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = ""
    token_type: str
