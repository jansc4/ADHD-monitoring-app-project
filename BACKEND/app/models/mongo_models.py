from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import Optional, Literal, List
from datetime import datetime


class UserInDB(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    password: str
    role: Literal["admin", "patient", "doctor"] = "patient"  # domyślnie każdy nowy użytkownik to patient
    created_at: Optional[datetime] = None
    doctor_id: Optional[str] = None  # ID lekarza przypisanego do pacjenta
    meta: Optional[dict] = Field(default_factory=dict)  # Dodatkowe dane użytkownika

    class Config:
        json_encoders = {
            ObjectId: str
        }