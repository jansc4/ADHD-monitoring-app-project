from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List

from app.models.mongo_models import UserInDB
from app.schemas.pydantic_schemas import (
    UserResponse
)
from app.security import get_current_user



router = APIRouter(prefix="/users")

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Zwraca dane zalogowanego użytkownika.
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
    }
""" @router.get("/user_profile", response_model=List[UserProfileResponse])
async def user_profile(current_user: dict = Depends(get_current_user)):

    check_role(current_user, "admin")
    return await get_all_profiles_service(db)


@router.get("/user_profile/{user_id}", response_model=UserProfileResponse)
async def user_profile_with_id(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    check_role(current_user, "admin")
    return await get_profile_by_id_service(user_id, db)


 """