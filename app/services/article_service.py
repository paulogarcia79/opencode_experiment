import uuid
import re
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models.article import Article
from app.models.tag import Tag
from app.services.content_service import auto_generate_description, extract_plain_text_from_tiptap
from app.services.search_service import build_search_text
from app.services.tag_service import get_or_create_tags

def generate_slug(title: str, session: Session) -> str:
    """Generate a unique URL slug from a title."""
    base = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    if not base:
        base = "article"
    
    slug = base
    counter = 2
    while session.exec(select(Article).where(Article.slug == slug)).first():
        slug = f"{base}-{counter}"
        counter += 1
    
    return slug

def create_article(
    session: Session,
    title: str,
    content: dict,
    description: Optional[str] = None,
    send_newsletter: bool = True,
    tag_names: Optional[List[str]] = None,
    scheduled_for: Optional[datetime] = None,
    author_id: Optional[uuid.UUID] = None,
) -> Article:
    slug = generate_slug(title, session)
    if description is None:
        description = auto_generate_description(content)
    
    tags = get_or_create_tags(session, tag_names or [])
    
    article = Article(
        title=title,
        slug=slug,
        content=content,
        description=description,
        status="draft",
        send_newsletter=send_newsletter,
        scheduled_for=scheduled_for,
        author_id=author_id,
        search_text=build_search_text(title, description, content, [t.name for t in tags]),
    )
    article.tags = tags
    session.add(article)
    session.commit()
    session.refresh(article)
    # Eager-load tags for serialization
    return session.exec(
        select(Article).where(Article.id == article.id).options(selectinload(Article.tags), selectinload(Article.author))
    ).first()

def get_article_by_slug(session: Session, slug: str) -> Optional[Article]:
    return session.exec(
        select(Article)
        .where(Article.slug == slug)
        .options(selectinload(Article.tags))
    ).first()

def list_published_articles(session: Session):
    return session.exec(
        select(Article)
        .where(Article.status == "published")
        .order_by(Article.published_at.desc())
        .options(selectinload(Article.tags))
    ).all()

def list_all_articles(session: Session):
    return session.exec(
        select(Article)
        .order_by(Article.created_at.desc())
        .options(selectinload(Article.tags))
    ).all()

def update_article(session: Session, article: Article, **kwargs) -> Article:
    tag_names = kwargs.pop("tag_names", None)
    for key, value in kwargs.items():
        if hasattr(article, key):
            setattr(article, key, value)
    
    if tag_names is not None:
        article.tags = get_or_create_tags(session, tag_names)
    
    # Rebuild search text if title, description, content, or tags changed
    article.search_text = build_search_text(
        article.title,
        article.description,
        article.content,
        [t.name for t in article.tags],
    )
    session.add(article)
    session.commit()
    session.refresh(article)
    # Eager-load tags for serialization
    return session.exec(
        select(Article).where(Article.id == article.id).options(selectinload(Article.tags))
    ).first()

def delete_article(session: Session, article: Article) -> None:
    from app.models.article_revision import ArticleRevision
    from app.models.article_view import ArticleView
    from app.models.newsletter_send import NewsletterSend

    # Delete related records first (for existing DBs without CASCADE)
    for rev in session.exec(select(ArticleRevision).where(ArticleRevision.article_id == article.id)):
        session.delete(rev)
    for view in session.exec(select(ArticleView).where(ArticleView.article_id == article.id)):
        session.delete(view)
    for send in session.exec(select(NewsletterSend).where(NewsletterSend.article_id == article.id)):
        session.delete(send)

    session.delete(article)
    session.commit()

def reassign_article(
    session: Session,
    article: Article,
    new_author_id: uuid.UUID,
) -> Article:
    """Reassign an article to a new author and create a revision."""
    from app.models.user import User
    from app.services.revision_service import create_revision

    old_author_id = article.author_id

    new_author = session.get(User, new_author_id)
    if not new_author:
        raise ValueError("Target user not found")

    if not new_author.is_active:
        raise ValueError("Target user is inactive")

    article.author_id = new_author_id
    session.add(article)
    session.commit()
    session.refresh(article)

    # Create revision with reassign metadata
    revision = create_revision(session, article, "reassign")
    revision.reassign_metadata = {
        "old_author_id": str(old_author_id) if old_author_id else None,
        "new_author_id": str(new_author_id),
    }
    session.add(revision)
    session.commit()
    session.refresh(revision)

    return session.exec(
        select(Article).where(Article.id == article.id).options(selectinload(Article.tags), selectinload(Article.author))
    ).first()
