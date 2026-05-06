import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field

class NewsletterSend(SQLModel, table=True):
    __tablename__ = "newsletter_sends"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    article_id: uuid.UUID = Field(foreign_key="articles.id", nullable=False)
    subscriber_id: uuid.UUID = Field(foreign_key="subscribers.id", nullable=False)
    sent_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
