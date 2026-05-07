import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class ImageAsset(SQLModel, table=True):
    __tablename__ = "image_assets"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    filename: str = Field(nullable=False)
    original_name: str = Field(nullable=False)
    mime_type: str = Field(nullable=False)
    size_bytes: int = Field(nullable=False)
    storage_path: str = Field(nullable=False)
    url: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
