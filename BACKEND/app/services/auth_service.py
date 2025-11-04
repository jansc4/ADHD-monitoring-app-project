from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.user_repository import *
from app.models import UserInDB
from app.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    verify_token
)
from app.schemas import (
    UserCreate, TokenResponse, UserResponse
)



async def register_user_service(user: UserCreate) -> UserResponse:
    await check_email(str(user.email))
    hashed_password = hash_password(user.password)
    new_user = UserInDB(username=user.username, email=user.email, password=hashed_password)
    await create_user(new_user.model_dump())
    return UserResponse(username=user.username, email=user.email)


async def login_user_service(form_data) -> TokenResponse:
    db_user = await get_user_by_email(form_data.username)
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_id = str(db_user["_id"])
    role = db_user.get("role", "user")
    access_token = create_access_token({"sub": user_id, "scopes": [role]})
    refresh_token = create_refresh_token({"sub": user_id})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


async def refresh_token_service(refresh_token: str) -> TokenResponse:
    payload = verify_token(refresh_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token({"sub": str(user["_id"]), "scopes": [user["role"]]})
    return TokenResponse(access_token=access_token, token_type="bearer")

def check_role(current_user: dict, required_role: str):
    """
    Sprawdza, czy użytkownik posiada wymaganą rolę.

    Args:
        current_user (dict): Dane użytkownika, który jest aktualnie zalogowany.
        required_role (str): Rola, którą użytkownik musi posiadać.

    Raises:
        HTTPException: Jeśli użytkownik nie ma wymaganej roli, zgłasza błąd 403 (Forbidden).
    """
    if required_role not in current_user.get("role", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDsEN,
            detail=f"Insufficient permissions. Required role: {required_role}",
        )
        
        
async def check_email(required_email: str):
    """
    Sprawdza, czy email jest już używany przez innego użytkownika w bazie danych.

    Args:
        required_email (str): Email, który ma zostać sprawdzony.
        db: Obiekt bazy danych.

    Raises:
        HTTPException: Jeśli email jest już w użyciu, zgłasza błąd 400 (Bad Request).
    """

    existing_user = await get_user_by_email(required_email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

async def check_id(required_id: str):
    """
    Sprawdza, czy użytkownik o podanym identyfikatorze istnieje w bazie danych.

    Args:
        required_id (str): ID użytkownika, którego istnienie ma zostać zweryfikowane.
        db: Obiekt bazy danych.

    Returns:
        dict: Dane użytkownika, jeśli istnieje.

    Raises:
        HTTPException: Jeśli użytkownik o danym ID nie istnieje, zgłasza błąd 404 (Not Found).
    """
    existing_user = await get_user_by_id(required_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    return existing_user