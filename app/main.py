from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database import create_db_and_tables

# Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.orders import router as orders_router

# Modelos (Necesarios para que SQLModel los registre al inicio)
from app.models.user import User
from app.models.inventory import Product, Category
from app.models.orders import Order, OrderItem

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando Sistema de Inventario Pro...")
    create_db_and_tables()
    yield
    print("Apagando sistema...")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Registro de rutas
app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(orders_router)

@app.get("/")
def home():
    return {"status": "Online", "version": "1.0.0"}