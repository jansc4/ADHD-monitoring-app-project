import logging
from fastapi import FastAPI
from app.routers import admin, doctors
from app.routers import patients
from app.routers import auth
from contextlib import asynccontextmanager
from app.db.mongo import connect_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()  # Połączenie z bazą danych przy starcie
    yield
    # Tu możesz dodać cleanup, np. zamknięcie połączeń

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


app = FastAPI(lifespan=lifespan)

# Rejestrowanie endpointów użytkowników
app.include_router(patients.router)
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the User API"}