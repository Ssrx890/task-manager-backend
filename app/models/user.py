from typing import Optional
from sqlmodel import SQLModel, Field

# Esquema base: campos comunes
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str
    role: str = "SELLER"  # Valores: ADMIN, SELLER

# Tabla de la base de datos
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

# Esquema para crear usuario (aquí sí pedimos password)
class UserCreate(UserBase):
    password: str

# Esquema para responder a la API (ocultamos el password)
class UserResponse(UserBase):
    id: int

# Esquemas para el Token JWT
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(SQLModel):
    email: Optional[str] = None
    role: Optional[str] = None