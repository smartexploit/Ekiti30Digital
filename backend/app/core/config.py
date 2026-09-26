from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    NEXTAUTH_SECRET: str = "default-secret-key"
    DATABASE_URL: str = "sqlite:///./test.db"
    
    CLOUDINARY_CLOUD_NAME: Optional[str] = "ekiti-test"
    CLOUDINARY_API_KEY: Optional[str] = "123456789"
    CLOUDINARY_API_SECRET: Optional[str] = "test-secret"
    CLOUDINARY_UPLOAD_PRESET: Optional[str] = "ekiti30_member_unsigned"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
