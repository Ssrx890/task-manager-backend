from sqlmodel import SQLModel, create_engine, Session
from .core.config import settings

# El 'engine' permite la comunicación con la BD
# 'check_same_thread' solo es necesario para SQLite
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Función para crear las tablas al iniciar el servidor
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Generador para obtener una sesión de BD en cada petición
def get_session():
    with Session(engine) as session:
        yield session