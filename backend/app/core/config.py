from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Database
    # Default to SQLite for easy development (no setup required)
    # For production, use PostgreSQL: postgresql://bnpl_user:bnpl_password@localhost:5432/bnpl_db
    DATABASE_URL: str = "sqlite:///./bnpl_dev.db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    # Comma-separated list of allowed origins, or "*" for all (development only)
    # Example: "https://app.example.com,https://www.example.com"
    CORS_ORIGINS: str = "*"  # Change to specific origins in production

    # API Keys
    RESEND_API_KEY: Optional[str] = None

    # Application
    APP_NAME: str = "BNPL Platform"
    DEBUG: bool = True
    DEV_SEED: bool = False  # Set to True to seed development accounts
    
    # Admin code for lender registration (due diligence)
    LENDER_ADMIN_CODE: str = "LENDER2024"  # Change this in production

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

