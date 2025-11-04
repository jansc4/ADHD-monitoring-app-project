from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Annotated, List

from app.db.mongo import get_db
from app.schemas import (
    UserCreate, UserResponse, TokenResponse,
    UserProfileResponse, UpdateUserProfile
)
from app.auth import get_current_user
from BACKEND.app.security import check_role

from app.services.user_service import (
    register_user_service,
    login_user_service,
    refresh_token_service,
    get_all_profiles_service,
    get_profile_by_id_service,
    get_profile_by_email_service,
    create_profile_service,
    update_profile_service,
    delete_profile_service
)

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}


@router.get("/user_profile", response_model=List[UserProfileResponse])
async def user_profile(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user: dict = Depends(get_current_user)
):
    check_role(current_user, "admin")
    return await get_all_profiles_service(db)


@router.get("/user_profile/{user_id}", response_model=UserProfileResponse)
async def user_profile_with_id(
    user_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    current_user: dict = Depends(get_current_user)
):
    check_role(current_user, "admin")
    return await get_profile_by_id_service(user_id, db)

# ... analogicznie reszta endpointów ...
