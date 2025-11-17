from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    # Default to SQLite for easy development (no setup required)
    # For production, use PostgreSQL: postgresql://bnpl_user:bnpl_password@localhost:5432/bnpl_db
    DATABASE_URL: str = "sqlite:///./bnpl_dev.db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    APP_NAME: str = "BNPL Platform"
    DEBUG: bool = True
    DEV_SEED: bool = False  # Set to True to seed development accounts

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

