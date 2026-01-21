from fastapi import FastAPI
from contextlib import asynccontextmanager

# --- IMPORTACIONES CLAVE ---
from .core.config import settings      # <--- ESTA ES LA QUE TE FALTA
from .database import create_db_and_tables
from .api.v1.auth import router as auth_router
from .models.user import User          # Importante para que SQLModel vea la tabla
# ---------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Acciones al iniciar
    print("Iniciando aplicación: Creando tablas...")
    create_db_and_tables()
    yield
    # Acciones al cerrar
    print("Cerrando aplicación...")

app = FastAPI(
    title=settings.PROJECT_NAME, # Aquí es donde fallaba porque no encontraba 'settings'
    lifespan=lifespan
)

# Rutas
app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "API de Inventario Pro activa"}