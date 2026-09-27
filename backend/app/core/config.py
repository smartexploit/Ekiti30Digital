import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ekiti30Digital"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-testing-purposes")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///./test.db")

    model_config = SettingsConfigDict(case_sensitive=True, extra="allow")

settings = Settings()
