from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Inventario Pro"
    SECRET_KEY: str = "CAMBIAME_POR_UNA_CLAVE_SUPER_SECRETA_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./database.db"

    class Config:
        env_file = ".env"

settings = Settings()