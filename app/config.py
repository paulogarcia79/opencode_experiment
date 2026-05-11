from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/blog"
    ADMIN_API_TOKEN: str = "dev-token-change-in-production"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin"
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production"
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "newsletter@example.com"
    RESEND_WEBHOOK_SECRET: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    APP_BASE_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:4173"]
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    # Branding
    SITE_NAME: str = "Impossible Code"
    SITE_LOGO_URL: str = "https://images.unsplash.com/photo-1614850523296-d8c1af93d400?w=300&h=300&fit=crop" # Placeholder neon logo
    BRAND_PRIMARY_COLOR: str = "#7C3AED"

    # Rate limiting
    RATE_LIMIT_SEARCH: str = "10/minute"
    RATE_LIMIT_SUBSCRIBE: str = "3/minute"
    RATE_LIMIT_ARTICLE_VIEW: str = "30/minute"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
