from fastapi import APIRouter, Depends, HTTPException, status
from app.models.mongo_models import UserInDB
from app.security import require_role
from app.schemas.pydantic_schemas import UserRole

router = APIRouter(prefix="/doctor", tags=["doctor"])

@router.get("/doctor")
async def read_doctor_data(current_user: UserInDB = Depends(require_role([UserRole.DOCTOR, UserRole.ADMIN]))):
    return {"message": "Welcome to the doctor panel!"}