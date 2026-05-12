import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Subscriber(SQLModel, table=True):
    __tablename__ = "subscribers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    status: str = Field(default="pending", nullable=False)  # "pending", "active", "unsubscribed"
    confirmation_token: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
