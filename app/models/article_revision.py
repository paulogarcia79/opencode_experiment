import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column, Text, Index

class ArticleRevision(SQLModel, table=True):
    __tablename__ = "article_revisions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    article_id: uuid.UUID = Field(foreign_key="articles.id", ondelete="CASCADE", nullable=False, index=True)
    version_number: int = Field(nullable=False)
    title: str = Field(nullable=False)
    content: dict = Field(default_factory=dict, sa_column=Column(JSON))
    description: str | None = Field(default=None, sa_column=Column(Text))
    tag_names: list = Field(default_factory=list, sa_column=Column(JSON))
    change_type: str = Field(nullable=False)  # "save", "publish", "restore"
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_article_revisions_article_version", "article_id", "version_number"),
    )
