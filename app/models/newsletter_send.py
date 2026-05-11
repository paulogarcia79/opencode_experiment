import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class NewsletterSend(SQLModel, table=True):
    __tablename__ = "newsletter_sends"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    article_id: uuid.UUID = Field(foreign_key="articles.id", nullable=False)
    subscriber_id: uuid.UUID = Field(foreign_key="subscribers.id", nullable=False)
    status: str = Field(default="pending", nullable=False)
    error_message: Optional[str] = Field(default=None, nullable=True)
    scheduled_at: Optional[datetime] = Field(default=None, nullable=True)
    sent_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
