from fastapi import APIRouter, Depends, HTTPException, status
from app.models.mongo_models import UserInDB
from app.security import require_role
from app.schemas.pydantic_schemas import UserRole

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/")
async def read_admin_data(current_user: UserInDB = Depends(require_role([UserRole.ADMIN]))):
    return {"message": "Welcome to the admin panel!"}