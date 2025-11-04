from bson import ObjectId
from fastapi import HTTPException, status

from models.mongo_models import UserInDB

""" from schemas.pydantic_schemas import (
    UserCreate, TokenResponse, UserResponse,
    UserProfileResponse, UpdateUserProfile
)
from BACKEND.app.security import check_email, check_id



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

 """
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
        