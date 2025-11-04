from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models import UserInDB
from app.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    verify_token
)
from app.schemas import (
    UserCreate, TokenResponse, UserResponse,
    UserProfileResponse, UpdateUserProfile
)
from BACKEND.app.security import check_email, check_id


async def register_user_service(user: UserCreate, db: AsyncIOMotorDatabase) -> UserResponse:
    await check_email(str(user.email), db)
    hashed_password = hash_password(user.password)
    new_user = UserInDB(username=user.username, email=user.email, password=hashed_password)
    await db.users.insert_one(new_user.model_dump())
    return UserResponse(username=user.username, email=user.email)


async def login_user_service(form_data, db: AsyncIOMotorDatabase) -> TokenResponse:
    db_user = await db.users.find_one({"email": form_data.username})
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_id = str(db_user["_id"])
    role = db_user.get("role", "user")
    access_token = create_access_token({"sub": user_id, "scopes": [role]})
    refresh_token = create_refresh_token({"sub": user_id})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


async def refresh_token_service(refresh_token: str, db: AsyncIOMotorDatabase) -> TokenResponse:
    payload = verify_token(refresh_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token({"sub": str(user["_id"]), "scopes": [user["role"]]})
    return TokenResponse(access_token=access_token, token_type="bearer")


async def get_all_profiles_service(db: AsyncIOMotorDatabase):
    users = await db.users.find().to_list(None)
    return [
        UserProfileResponse(username=u["username"], email=u["email"], id=str(u["_id"]), role=u["role"])
        for u in users
    ]


async def get_profile_by_id_service(user_id: str, db: AsyncIOMotorDatabase):
    user = await check_id(user_id, db)
    return UserProfileResponse(username=user["username"], email=user["email"], id=user_id, role=user["role"])


async def get_profile_by_email_service(email: str, db: AsyncIOMotorDatabase):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfileResponse(username=user["username"], email=user["email"], id=str(user["_id"]), role=user["role"])


async def create_profile_service(user: UpdateUserProfile, db: AsyncIOMotorDatabase):
    await check_email(user.email, db)
    hashed_password = hash_password(user.password)
    new_user = UserInDB(username=user.username, email=user.email, password=hashed_password, role=user.role)
    result = await db.users.insert_one(new_user.model_dump())
    return UserProfileResponse(username=user.username, email=user.email, id=str(result.inserted_id), role=user.role)


async def update_profile_service(user_id: str, user: UpdateUserProfile, db: AsyncIOMotorDatabase):
    await check_id(user_id, db)
    updated_user = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role
    }
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_user})
    return UserProfileResponse(username=user.username, email=user.email, id=user_id, role=user.role)


async def delete_profile_service(user_id: str, db: AsyncIOMotorDatabase):
    existing_user = await check_id(user_id, db)
    await db.users.delete_one({"_id": ObjectId(user_id)})
    return UserProfileResponse(
        username=existing_user["username"],
        email=existing_user["email"],
        id=user_id,
        role=existing_user["role"]
    )
