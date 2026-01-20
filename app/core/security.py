from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from .config import settings

# Configuramos cómo se van a hashear las contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para encriptar una contraseña plana (al registrarse)
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Función para verificar si una contraseña coincide con el hash (al login)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Función para crear el token JWT que el usuario usará para identificarse
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt