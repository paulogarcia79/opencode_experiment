import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, UniqueConstraint

class UserOAuthProvider(SQLModel, table=True):
    __tablename__ = "user_oauth_providers"
    __table_args__ = (UniqueConstraint("provider", "provider_user_id", name="uq_provider_user_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    provider: str = Field(nullable=False)
    provider_user_id: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
