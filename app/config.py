from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Keys
    MOBILE_MONEY_API_KEY: Optional[str] = None
    BANK_API_KEY: Optional[str] = None
    VISA_API_KEY: Optional[str] = None
    MASTERCARD_API_KEY: Optional[str] = None
    NIN_VERIFICATION_API_KEY: Optional[str] = None
    KYC_VERIFICATION_API_KEY: Optional[str] = None
    RESEND_API_KEY: Optional[str] = None

    # Application
    DEBUG: bool = True
    APP_NAME: str = "BNPL Platform"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

