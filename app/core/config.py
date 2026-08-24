from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./crm.db"
    DATABASE_ECHO: bool = True # Ver SQL e consola ( solo desarrollo)

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App 
    APP_NAME: str = "CRM System"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()