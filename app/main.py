from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import create_db_and_tables
from .core.config import settings

# ⚠️ Importante: para que SQLModel registre las tablas
from .models.user import User  


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación: Creando tablas...")
    create_db_and_tables()
    yield
    print("Cerrando aplicación: Limpiando recursos...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {
        "message": "API de Inventario Pro activa y usando Lifespan Events"
    }
