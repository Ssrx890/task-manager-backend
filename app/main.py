from fastapi import FastAPI
from .api.v1.auth import router as auth_router # Importar el router
# ... (otros imports)

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Registrar las rutas de autenticación
app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "API de Inventario Pro activa"}