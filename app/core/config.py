from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    PROJECT_NAME: str = "Sistema de Inventario Pro"
    SECRET_KEY: str  # Obligatorio — debe configurarse en .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./database.db"
    INITIAL_ADMIN_EMAIL: str = "admin@tuempresa.com"
    INITIAL_ADMIN_PASSWORD: str  # Obligatorio — debe configurarse en .env
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"


settings = Settings()