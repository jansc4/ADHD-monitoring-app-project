from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_user_by_email(email: str, db: AsyncIOMotorDatabase):
    return await db.users.find_one({"email": email})

async def get_user_by_id(user_id: str, db: AsyncIOMotorDatabase):
    return await db.users.find_one({"_id": ObjectId(user_id)})

async def create_user(user_data: dict, db: AsyncIOMotorDatabase):
    result = await db.users.insert_one(user_data)
    return str(result.inserted_id)

async def update_user(user_id: str, new_data: dict, db: AsyncIOMotorDatabase):
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": new_data})

async def delete_user(user_id: str, db: AsyncIOMotorDatabase):
    return await db.users.delete_one({"_id": ObjectId(user_id)})
