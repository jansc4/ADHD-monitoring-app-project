from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List

from app.models.mongo_models import UserInDB
from app.schemas.pydantic_schemas import (
    UserResponse,
    UserRole
)
from app.security import get_current_user, require_role



router = APIRouter(prefix="/patient", tags=["patient"])

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT]))):
    """
    Zwraca dane zalogowanego użytkownika.
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
    }
