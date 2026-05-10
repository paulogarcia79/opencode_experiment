import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String

class ArticleTag(SQLModel, table=True):
    __tablename__ = "article_tags"

    article_id: uuid.UUID = Field(foreign_key="articles.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String, unique=True, nullable=False))
    slug: str = Field(sa_column=Column(String, unique=True, nullable=False, index=True))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    articles: List["Article"] = Relationship(back_populates="tags", link_model=ArticleTag)
