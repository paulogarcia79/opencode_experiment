import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class ArticleView(SQLModel, table=True):
    __tablename__ = "article_views"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    article_id: uuid.UUID = Field(foreign_key="articles.id", ondelete="CASCADE", nullable=False, index=True)
    ip_hash: str = Field(nullable=False)
    viewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
