from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database import create_db_and_tables

# Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.orders import router as orders_router
from app.api.v1.finance import router as finance_router

# Modelos para SQLModel
from app.models.user import User
from app.models.inventory import Product, Category
from app.models.orders import Order, OrderItem
from app.models.finance import Debt, Payment

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando Sistema de Gestión de Negocio...")
    create_db_and_tables()
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(finance_router)

@app.get("/")
def home():
    return {"status": "Sistema de Negocio Online"}