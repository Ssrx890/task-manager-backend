import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select

# Importaciones Absolutas (Arquitectura Senior)
from app.core.config import settings
from app.database import engine, create_db_and_tables
from app.core.security import get_password_hash

# Importación de Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.orders import router as orders_router
from app.api.v1.finance import router as finance_router
from app.api.v1.cart import router as cart_router

# Importación de Modelos (Obligatorio para que SQLModel cree las tablas)
from app.models.user import User
from app.models.inventory import Product, Category
from app.models.orders import Order, OrderItem
from app.models.finance import Debt, Payment
from app.models.cart import Cart, CartItem

# --- CONFIGURACIÓN DEL CICLO DE VIDA (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el arranque y cierre de la aplicación"""
    print("Iniciando Sistema de Gestión de Negocio...")
    
    # 1. Crear tablas si no existen
    create_db_and_tables()
    
    # 2. LÓGICA DE SEEDING: Crear el primer admin desde el .env si la BD está vacía
    with Session(engine) as session:
        # Buscamos si ya existe algún usuario
        user_exists = session.exec(select(User)).first()
        
        if not user_exists:
            print(f"⚠️ No se encontraron usuarios. Creando Administrador Inicial: {settings.INITIAL_ADMIN_EMAIL}")
            
            first_admin = User(
                email=settings.INITIAL_ADMIN_EMAIL,
                full_name="Administrador del Sistema",
                hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                role="ADMIN"
            )
            session.add(first_admin)
            session.commit()
            print("✅ Administrador inicial creado con éxito.")
        else:
            print("ℹ️ Base de datos ya cuenta con usuarios registrados.")
            
    yield
    print("Apagando Sistema...")

# --- INSTANCIA DE LA APLICACIÓN ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# --- CONFIGURACIÓN DE CORS (Para Web y Flutter) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción reemplazar con dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ARCHIVOS ESTÁTICOS (Imágenes de productos) ---
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- REGISTRO DE RUTAS (ROUTERS) ---
app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(finance_router)
app.include_router(cart_router)

# --- RUTA DE SALUD ---
@app.get("/", tags=["General"])
def read_root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "Online",
        "documentation": "/docs"
    }