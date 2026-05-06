import uuid
import re
from typing import Optional
from sqlmodel import Session, select
from app.models.article import Article
from app.services.content_service import auto_generate_description

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

def create_article(session: Session, title: str, content: dict, description: Optional[str] = None, send_newsletter: bool = True) -> Article:
    slug = generate_slug(title, session)
    if description is None:
        description = auto_generate_description(content)
    article = Article(
        title=title,
        slug=slug,
        content=content,
        description=description,
        status="draft",
        send_newsletter=send_newsletter,
    )
    session.add(article)
    session.commit()
    session.refresh(article)
    return article

def get_article_by_slug(session: Session, slug: str) -> Optional[Article]:
    return session.exec(select(Article).where(Article.slug == slug)).first()

def list_published_articles(session: Session):
    return session.exec(
        select(Article)
        .where(Article.status == "published")
        .order_by(Article.published_at.desc())
    ).all()

def list_all_articles(session: Session):
    return session.exec(
        select(Article)
        .order_by(Article.created_at.desc())
    ).all()

def update_article(session: Session, article: Article, **kwargs) -> Article:
    for key, value in kwargs.items():
        if hasattr(article, key):
            setattr(article, key, value)
    session.add(article)
    session.commit()
    session.refresh(article)
    return article

def delete_article(session: Session, article: Article) -> None:
    session.delete(article)
    session.commit()
