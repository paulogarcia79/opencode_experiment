import uuid
from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import Session, select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from app.models.article import Article
from app.models.article_revision import ArticleRevision
from app.services.tag_service import get_or_create_tags
from app.services.content_service import extract_plain_text_from_tiptap
from app.services.search_service import build_search_text


def _next_version_number(session: Session, article_id: uuid.UUID) -> int:
    """Get the next version number for an article (max + 1, or 1 if none exist)."""
    result = session.exec(
        select(func.max(ArticleRevision.version_number))
        .where(ArticleRevision.article_id == article_id)
    ).first()
    return (result or 0) + 1


def create_revision(
    session: Session,
    article: Article,
    change_type: str,
) -> ArticleRevision:
    """Create a revision snapshot of the current article state."""
    version_number = _next_version_number(session, article.id)
    tag_names = [tag.name for tag in article.tags]

    revision = ArticleRevision(
        article_id=article.id,
        version_number=version_number,
        title=article.title,
        content=article.content,
        description=article.description,
        tag_names=tag_names,
        change_type=change_type,
        created_at=datetime.now(timezone.utc),
    )
    session.add(revision)
    session.commit()
    session.refresh(revision)
    return revision


def list_revisions(session: Session, article_id: uuid.UUID) -> List[ArticleRevision]:
    """List all revisions for an article, newest first."""
    return session.exec(
        select(ArticleRevision)
        .where(ArticleRevision.article_id == article_id)
        .order_by(ArticleRevision.version_number.desc())
    ).all()


def get_revision(
    session: Session,
    article_id: uuid.UUID,
    version_number: int,
) -> Optional[ArticleRevision]:
    """Get a single revision by article_id and version_number."""
    return session.exec(
        select(ArticleRevision)
        .where(ArticleRevision.article_id == article_id)
        .where(ArticleRevision.version_number == version_number)
    ).first()


def restore_revision(
    session: Session,
    article: Article,
    version_number: int,
) -> Article:
    """Restore an article to a previous revision state.

    Restores title, content, description, and tags. Does NOT change
    status, published_at, send_newsletter, or scheduled_for.
    Creates a new 'restore' revision entry after restoration.
    """
    revision = get_revision(session, article.id, version_number)
    if not revision:
        return None

    article.title = revision.title
    article.content = revision.content
    article.description = revision.description

    article.tags = get_or_create_tags(session, revision.tag_names) if revision.tag_names else []

    article.search_text = build_search_text(
        article.title,
        article.description,
        article.content,
        [t.name for t in article.tags],
    )

    session.add(article)
    session.commit()
    session.refresh(article)

    article = session.exec(
        select(Article)
        .where(Article.id == article.id)
        .options(selectinload(Article.tags))
    ).first()

    create_revision(session, article, "restore")
    return session.exec(
        select(Article)
        .where(Article.id == article.id)
        .options(selectinload(Article.tags))
    ).first()
