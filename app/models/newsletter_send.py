import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class NewsletterSend(SQLModel, table=True):
    __tablename__ = "newsletter_sends"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    article_id: uuid.UUID = Field(foreign_key="articles.id", ondelete="CASCADE", nullable=False, index=True)
    subscriber_id: uuid.UUID = Field(foreign_key="subscribers.id", nullable=False, index=True)
    status: str = Field(default="pending", nullable=False)
    error_message: Optional[str] = Field(default=None, nullable=True)
    scheduled_at: Optional[datetime] = Field(default=None, nullable=True)
    opened_at: Optional[datetime] = Field(default=None, nullable=True)
    clicked_at: Optional[datetime] = Field(default=None, nullable=True)
    open_count: int = Field(default=0, nullable=False)
    click_count: int = Field(default=0, nullable=False)
    sent_at: Optional[datetime] = Field(default=None, nullable=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
