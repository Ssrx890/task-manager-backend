from typing import Optional
from sqlmodel import SQLModel, Field

# Esquema base que comparten la BD y la API
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str
    role: str = "SELLER"  # Roles: ADMIN, SELLER

# Cómo se guarda en la base de datos (con contraseña hashed)
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

# Qué devuelve la API al crear un usuario (nunca devolvemos la contraseña)
class UserResponse(UserBase):
    id: int