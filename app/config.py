from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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

    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # Debug/Dev
    SQL_ECHO: bool = False

    @field_validator("ADMIN_API_TOKEN")
    @classmethod
    def validate_admin_token(cls, v: str) -> str:
        if v == "dev-token-change-in-production":
            import os
            if os.getenv("APP_ENV", "development") != "development":
                raise ValueError("ADMIN_API_TOKEN must be set to a secure value in production")
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if v == "super-secret-key-change-in-production":
            import os
            if os.getenv("APP_ENV", "development") != "development":
                raise ValueError("JWT_SECRET_KEY must be set to a secure value in production")
        return v

    @field_validator("ADMIN_PASSWORD")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        if v == "admin":
            import os
            if os.getenv("APP_ENV", "development") != "development":
                raise ValueError("ADMIN_PASSWORD must be set to a secure value in production")
        return v

settings = Settings()
