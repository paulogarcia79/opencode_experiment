from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/blog"
    ADMIN_API_TOKEN: str = "dev-token-change-in-production"
    ADMIN_EMAIL: str = "admin@example.com"
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "newsletter@example.com"
    APP_BASE_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:4173"]
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
