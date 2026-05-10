from datetime import timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session
from app.database import get_session
from app.dependencies import require_admin
from app.models.article import Article
from app.schemas import ArticleCreate, ArticleUpdate, ArticleAutoSave, TagRead
from app.services.article_service import (
    create_article,
    get_article_by_slug,
    list_published_articles,
    list_all_articles,
    update_article,
    delete_article,
)
from app.services.newsletter_service import send_newsletter_for_article
from app.services.search_service import search_articles
from app.services.tag_service import get_or_create_tags
from app.services.email_service import send_newsletter_email
from app.services.tiptap_renderer import render_tiptap_to_email_html
from app.models.tag import Tag, ArticleTag
from app.config import settings

router = APIRouter()

# Public endpoints

@router.get("/api/articles", response_model=list[Article])
def list_articles_endpoint(session: Session = Depends(get_session)):
    return list_published_articles(session)

@router.get("/api/articles/search", response_model=list[Article])
def search_articles_endpoint(q: Optional[str] = None, session: Session = Depends(get_session)):
    if not q or not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' is required and must not be empty",
        )
    return search_articles(session, q.strip())

@router.get("/api/articles/{slug}")
def get_article_endpoint(slug: str, session: Session = Depends(get_session)):
    article = get_article_by_slug(session, slug)
    if not article or article.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    return response

@router.get("/feed.xml")
def rss_feed_endpoint(session: Session = Depends(get_session)):
    """Generate an Atom RSS feed of published articles."""
    articles = list_published_articles(session)
    base_url = settings.APP_BASE_URL.rstrip("/")
    site_title = "Tech & Games Blog"
    site_description = "Deep dives into software development, game design, and the technology shaping our digital world."

    def escape_xml(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    entries = []
    for article in articles:
        updated = (article.updated_at or article.created_at).replace(tzinfo=timezone.utc).isoformat()
        pub_date = article.published_at.replace(tzinfo=timezone.utc).isoformat() if article.published_at else updated
        link = f"{base_url}/articles/{article.slug}"
        title = escape_xml(article.title)
        summary = escape_xml(article.description or "")
        entries.append(f"""    <entry>
      <title>{title}</title>
      <link href="{link}" />
      <id>{link}</id>
      <updated>{updated}</updated>
      <published>{pub_date}</published>
      <summary>{summary}</summary>
    </entry>""")

    feed_updated = entries and articles[0].updated_at.replace(tzinfo=timezone.utc).isoformat() or ""

    atom_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{escape_xml(site_title)}</title>
  <link href="{base_url}/feed.xml" rel="self" />
  <link href="{base_url}" />
  <id>{base_url}/</id>
  <updated>{feed_updated}</updated>
  <subtitle>{escape_xml(site_description)}</subtitle>
{chr(10).join(entries)}
</feed>
"""
    return Response(content=atom_xml, media_type="application/atom+xml")

@router.get("/sitemap.xml")
def sitemap_endpoint(session: Session = Depends(get_session)):
    """Generate an XML sitemap of published articles.

    Future: split into <sitemapindex> when exceeding 49,999 URLs.
    """
    articles = list_published_articles(session)
    base_url = settings.APP_BASE_URL.rstrip("/")

    latest_published = max(
        (a.published_at for a in articles if a.published_at),
        default=None,
    )
    latest_lastmod = latest_published.replace(tzinfo=timezone.utc).isoformat() if latest_published else ""

    urls = [f"""  <url>
    <loc>{base_url}/</loc>
    <lastmod>{latest_lastmod}</lastmod>
  </url>"""]

    for article in articles:
        lastmod = (article.updated_at or article.created_at).replace(tzinfo=timezone.utc).isoformat()
        urls.append(f"""  <url>
    <loc>{base_url}/articles/{article.slug}</loc>
    <lastmod>{lastmod}</lastmod>
  </url>""")

    if articles:
        urls.append(f"""  <url>
    <loc>{base_url}/feed.xml</loc>
    <lastmod>{latest_lastmod}</lastmod>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    return Response(content=sitemap_xml, media_type="application/xml")

@router.get("/robots.txt")
def robots_txt_endpoint():
    """Return robots.txt with crawl rules and sitemap reference."""
    base_url = settings.APP_BASE_URL.rstrip("/")
    robots = f"""User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /uploads/
Sitemap: {base_url}/sitemap.xml
"""
    return Response(content=robots, media_type="text/plain; charset=utf-8")

# Admin endpoints

@router.post("/api/admin/articles", dependencies=[Depends(require_admin)])
def create_article_endpoint(
    data: ArticleCreate,
    session: Session = Depends(get_session),
):
    article = create_article(session, data.title, data.content, data.description, data.send_newsletter, data.tag_names)
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    return response

@router.get("/api/admin/articles", response_model=list[Article], dependencies=[Depends(require_admin)])
def list_admin_articles_endpoint(session: Session = Depends(get_session)):
    return list_all_articles(session)

@router.get("/api/admin/articles/{article_id}", dependencies=[Depends(require_admin)])
def get_admin_article_endpoint(article_id: UUID, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    return response

@router.put("/api/articles/{article_id}", dependencies=[Depends(require_admin)])
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
    if data.tag_names is not None:
        update_data["tag_names"] = data.tag_names
    
    updated = update_article(session, article, **update_data)
    
    # Serialize response before potential session commit in newsletter send
    response_data = updated.model_dump()
    response_data["tags"] = [TagRead.model_validate(t).model_dump() for t in updated.tags]
    
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

@router.post("/api/admin/articles/autosave", dependencies=[Depends(require_admin)])
def autosave_create_article_endpoint(
    data: ArticleAutoSave,
    session: Session = Depends(get_session),
):
    article = create_article(
        session,
        data.title or "Untitled",
        data.content or {"type": "doc", "content": [{"type": "paragraph"}]},
        data.description,
        send_newsletter=False,
        tag_names=data.tag_names,
    )
    response_data = article.model_dump()
    response_data["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    return response_data

@router.put("/api/admin/articles/{article_id}/autosave", dependencies=[Depends(require_admin)])
def autosave_article_endpoint(
    article_id: UUID,
    data: ArticleAutoSave,
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    update_data = {}
    if data.title is not None:
        update_data["title"] = data.title
    if data.content is not None:
        update_data["content"] = data.content
    if data.description is not None:
        update_data["description"] = data.description
    if data.tag_names is not None:
        update_data["tag_names"] = data.tag_names

    # Auto-save always keeps the article as a draft
    update_data["status"] = "draft"
    update_data["published_at"] = None

    updated = update_article(session, article, **update_data)

    response_data = updated.model_dump()
    response_data["tags"] = [TagRead.model_validate(t).model_dump() for t in updated.tags]
    return response_data

# Tag admin endpoints

@router.get("/api/admin/tags", dependencies=[Depends(require_admin)])
def list_tags_endpoint(q: Optional[str] = None, session: Session = Depends(get_session)):
    from sqlmodel import select, func
    statement = select(Tag)
    if q:
        statement = statement.where(Tag.name.ilike(f"%{q}%"))
    tags = session.exec(statement).all()
    # Count articles per tag
    result = []
    for tag in tags:
        article_count = session.exec(
            select(func.count(ArticleTag.article_id)).where(ArticleTag.tag_id == tag.id)
        ).first()
        tag_data = TagRead.model_validate(tag).model_dump()
        tag_data["article_count"] = article_count or 0
        result.append(tag_data)
    return result

@router.delete("/api/admin/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_tag_endpoint(tag_id: UUID, session: Session = Depends(get_session)):
    from sqlmodel import select, func
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    article_count = session.exec(
        select(func.count(ArticleTag.article_id)).where(ArticleTag.tag_id == tag.id)
    ).first() or 0
    if article_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Tag is in use", "article_count": article_count},
        )
    session.delete(tag)
    session.commit()
    return None

@router.post("/api/admin/articles/{article_id}/preview-email", dependencies=[Depends(require_admin)])
def preview_email_endpoint(article_id: UUID, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    
    html = render_tiptap_to_email_html(article.content)
    # Use dummy unsubscribe token for preview
    send_newsletter_email(settings.ADMIN_EMAIL, article.title, html, "preview-mode-no-unsubscribe")
    return {"message": "Preview sent successfully"}

# Public tag endpoints

@router.get("/api/tags/{slug}")
def get_tag_endpoint(slug: str, session: Session = Depends(get_session)):
    from sqlalchemy.orm import selectinload
    from sqlmodel import select
    tag = session.exec(select(Tag).where(Tag.slug == slug)).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    articles = session.exec(
        select(Article)
        .join(ArticleTag)
        .where(ArticleTag.tag_id == tag.id)
        .where(Article.status == "published")
        .options(selectinload(Article.tags))
    ).all()
    return {
        "name": tag.name,
        "slug": tag.slug,
        "articles": [a.model_dump() | {"tags": [TagRead.model_validate(t).model_dump() for t in a.tags]} for a in articles],
    }
