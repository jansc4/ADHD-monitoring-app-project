from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.pydantic_schemas import (
    UserCreate, UserResponse, TokenResponse
)

from app.services.auth_service import (
    register_user_service,
    login_user_service,
    refresh_token_service,
)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    return await register_user_service(user)


@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()
):
    return await login_user_service(form_data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    return await refresh_token_service(refresh_token)
