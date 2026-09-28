import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ekiti30Digital"
    API_V1_STR: str = "/api/v1"
    
    # Security Secrets
    SECRET_KEY: str = "test-secret-key-1234567890-32-bytes"
    ADMIN_JWT_SECRET: str = "test-secret-key-1234567890-32-bytes"
    JWT_SECRET: str = "test-secret-key-1234567890-32-bytes"
    NEXTAUTH_SECRET: str = "test-secret-key-1234567890-32-bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # Database
    DATABASE_URL: Optional[str] = "sqlite:///./test.db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///./test.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return []

    # Cloudinary Integration
    CLOUDINARY_CLOUD_NAME: Optional[str] = "test-cloud"
    CLOUDINARY_API_KEY: Optional[str] = "123456789"
    CLOUDINARY_API_SECRET: Optional[str] = "test-secret"
    CLOUDINARY_UPLOAD_PRESET: Optional[str] = "test-preset"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
