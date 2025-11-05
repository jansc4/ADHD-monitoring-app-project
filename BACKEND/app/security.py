from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from app.repositories.user_repository import get_user_by_id
from app.db.mongo import get_db
from bson import ObjectId
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.models.mongo_models import UserInDB
from motor.motor_asyncio import AsyncIOMotorDatabase

# Ustawiamy scope'y tutaj
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", scopes={
    "user": "Standard user",
    "admin": "Administrator access"
})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashuje hasło przy użyciu algorytmu bcrypt.

    Args:
        password (str): Hasło do zahaszowania.

    Returns:
        str: Zahaszowane hasło.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Weryfikuje, czy podane hasło pasuje do zahaszowanego.

    Args:
        plain_password (str): Hasło wprowadzone przez użytkownika.
        hashed_password (str): Zahaszowane hasło w bazie danych.

    Returns:
        bool: True, jeśli hasło jest poprawne, w przeciwnym razie False.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Tworzy access token z danymi użytkownika i czasem wygaśnięcia.

    Args:
        data (dict): Dane użytkownika, które mają być zapisane w tokenie.
        expires_delta (timedelta, optional): Czas, po którym token wygaśnie.

    Returns:
        str: Wygenerowany access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    """
    Tworzy refresh token z danymi użytkownika i czasem wygaśnięcia.

    Args:
        data (dict): Dane użytkownika, które mają być zapisane w tokenie.

    Returns:
        str: Wygenerowany refresh token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """
    Weryfikuje i dekoduje token.

    Args:
        token (str): Token do weryfikacji.

    Returns:
        dict: Dekodowane dane tokenu lub None w przypadku błędu.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None



async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> UserInDB:
    """
    Pobiera aktualnego użytkownika z bazy na podstawie tokenu JWT.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidłowy token uwierzytelniający",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(user_id, db)
    if user is None:
        raise credentials_exception

    return UserInDB(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        role=user["role"],
        password=user["password"],
    )


