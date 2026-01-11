import logging
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_db
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_id
)
from app.models.mongo_models import UserInDB
from app.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    verify_token
)
from app.schemas.pydantic_schemas import (
    UserCreate, TokenResponse, UserResponse
)

# Setup logger
logger = logging.getLogger(__name__)


# =========================
# REGISTER
# =========================
async def register_user_service(user: UserCreate) -> UserResponse:
    db = await get_db()

    # sprawdzenie emaila
    await check_email(str(user.email), db)

    hashed_password = hash_password(user.password)

    # ✅ WALIDACJA I ZAPIS ROLI
    role = user.role if user.role in ["patient", "doctor"] else "patient"

    new_user = UserInDB(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=role
    )

    await create_user(new_user.model_dump(), db)

    logger.info(f"User registered: {user.email} (role={role})")

    # 🔥 TU BYŁ PROBLEM — TERAZ JEST POPRAWNIE
    return UserResponse(
        username=user.username,
        email=user.email,
        role=role
    )


# =========================
# LOGIN
# =========================
async def login_user_service(form_data) -> TokenResponse:
    try:
        db = await get_db()
        logger.info(f"Attempting login for user: {form_data.username}")

        db_user = await get_user_by_email(form_data.username, db)
        if not db_user:
            logger.warning(f"Login failed - user not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not verify_password(form_data.password, db_user["password"]):
            logger.warning(f"Login failed - invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        user_id = str(db_user["_id"])
        role = db_user.get("role", "patient")

        logger.info(
            f"Login successful: {form_data.username} "
            f"(id={user_id}, role={role})"
        )

        access_token = create_access_token({
            "sub": user_id,
            "role": role
        })
        refresh_token = create_refresh_token({
            "sub": user_id
        })

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during login: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# =========================
# REFRESH TOKEN
# =========================
async def refresh_token_service(refresh_token: str) -> TokenResponse:
    payload = verify_token(refresh_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token({
        "sub": str(user["_id"]),
        "role": user.get("role", "patient")
    })

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


# =========================
# HELPERS
# =========================
async def check_email(required_email: str, db: AsyncIOMotorDatabase):
    existing_user = await get_user_by_email(required_email, db)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already in use"
        )


async def check_id(required_id: str, db: AsyncIOMotorDatabase):
    existing_user = await get_user_by_id(required_id, db)
    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return existing_user
