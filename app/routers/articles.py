from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.dependencies import require_admin
from app.models.article import Article
from app.schemas import ArticleCreate, ArticleUpdate
from app.services.article_service import (
    create_article,
    get_article_by_slug,
    list_published_articles,
    list_all_articles,
    update_article,
    delete_article,
)
from app.services.newsletter_service import send_newsletter_for_article

router = APIRouter()

# Public endpoints

@router.get("/api/articles", response_model=list[Article])
def list_articles_endpoint(session: Session = Depends(get_session)):
    return list_published_articles(session)

@router.get("/api/articles/{slug}", response_model=Article)
def get_article_endpoint(slug: str, session: Session = Depends(get_session)):
    article = get_article_by_slug(session, slug)
    if not article or article.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article

# Admin endpoints

@router.post("/api/admin/articles", response_model=Article, dependencies=[Depends(require_admin)])
def create_article_endpoint(
    data: ArticleCreate,
    session: Session = Depends(get_session),
):
    return create_article(session, data.title, data.content, data.description, data.send_newsletter)

@router.get("/api/admin/articles", response_model=list[Article], dependencies=[Depends(require_admin)])
def list_admin_articles_endpoint(session: Session = Depends(get_session)):
    return list_all_articles(session)

@router.get("/api/admin/articles/{article_id}", response_model=Article, dependencies=[Depends(require_admin)])
def get_admin_article_endpoint(article_id: UUID, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article

@router.put("/api/articles/{article_id}", response_model=Article, dependencies=[Depends(require_admin)])
def update_article_endpoint(
    article_id: UUID,
    data: ArticleUpdate,
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    
    should_send_newsletter = False
    
    if data.status == "published" and article.status == "draft":
        from datetime import datetime, timezone
        article.published_at = datetime.now(timezone.utc)
        should_send_newsletter = article.send_newsletter if data.send_newsletter is None else data.send_newsletter
    elif data.status == "draft" and article.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unpublish an article",
        )
    
    update_data = {}
    if data.title is not None:
        update_data["title"] = data.title
    if data.content is not None:
        update_data["content"] = data.content
    if data.description is not None:
        update_data["description"] = data.description
    if data.status is not None:
        update_data["status"] = data.status
    if data.send_newsletter is not None:
        update_data["send_newsletter"] = data.send_newsletter
    
    updated = update_article(session, article, **update_data)
    
    # Serialize response before potential session commit in newsletter send
    response_data = updated.model_dump()
    
    if should_send_newsletter:
        send_newsletter_for_article(session, updated)
    
    return response_data

@router.delete("/api/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_article_endpoint(article_id: UUID, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    delete_article(session, article)
    return None
