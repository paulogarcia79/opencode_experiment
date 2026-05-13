import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column, Text
from app.models.tag import ArticleTag

class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)
    content: dict = Field(default_factory=dict, sa_column=Column(JSON))
    description: Optional[str] = Field(default=None)
    status: str = Field(default="draft", nullable=False)  # "draft", "pending_review", or "published"
    send_newsletter: bool = Field(default=True, nullable=False)
    published_at: Optional[datetime] = Field(default=None)
    submitted_at: Optional[datetime] = Field(default=None, nullable=True)
    scheduled_for: Optional[datetime] = Field(default=None, nullable=True)
    search_text: Optional[str] = Field(default=None, sa_column=Column(Text))
    author_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id", nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    tags: List["Tag"] = Relationship(back_populates="articles", link_model=ArticleTag)
    author: Optional["User"] = Relationship(back_populates="articles")
