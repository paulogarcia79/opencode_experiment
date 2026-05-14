from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, UploadFile, File, Request
from sqlmodel import Session, select, func
from app.database import get_session
from app.dependencies import require_role, require_role_allow_unverified, get_arq_pool, _decode_and_validate_user
from arq.connections import ArqRedis
from app.models import Article, NewsletterSend, Tag, ArticleTag, ArticleRevision, ReviewAction
from app.schemas import ArticleCreate, ArticleUpdate, ArticleAutoSave, TagRead, RevisionListRead, RevisionRead, ImportResult, ArticleReassignRequest, ReviewRejectRequest
from app.services.article_service import (
    create_article,
    get_article_by_slug,
    list_published_articles,
    list_all_articles,
    update_article,
    delete_article,
    reassign_article,
)
from app.services.permission_service import check_article_permission
from app.services.revision_service import (
    list_revisions,
    get_revision,
    create_revision,
    restore_revision,
)
from app.services.newsletter_service import send_newsletter_for_article
from app.services.search_service import search_articles
from app.services.tag_service import get_or_create_tags
from app.services.email_service import send_newsletter_email
from app.services.tiptap_renderer import render_tiptap_to_email_html
from app.services.view_tracking_service import record_view
from app.models.tag import Tag, ArticleTag
from app.models import ArticleView
from app.config import settings
from app.limiter import limiter

router = APIRouter()

# Public endpoints

@router.get("/api/articles", response_model=list[Article])
def list_articles_endpoint(skip: int = 0, limit: int = 50, session: Session = Depends(get_session)):
    from sqlmodel import select
    from sqlalchemy.orm import selectinload
    limit = min(limit, 200)
    return session.exec(
        select(Article)
        .where(Article.status == "published")
        .order_by(Article.published_at.desc())
        .offset(skip)
        .limit(limit)
        .options(selectinload(Article.tags))
    ).all()

@router.get("/api/articles/search", response_model=list[Article])
@limiter.limit(settings.RATE_LIMIT_SEARCH)
def search_articles_endpoint(request: Request, q: Optional[str] = None, session: Session = Depends(get_session)):
    if not q or not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' is required and must not be empty",
        )
    return search_articles(session, q.strip())

@router.get("/api/articles/{slug}")
@limiter.limit(settings.RATE_LIMIT_ARTICLE_VIEW)
def get_article_endpoint(request: Request, slug: str, session: Session = Depends(get_session)):
    article = get_article_by_slug(session, slug)
    if not article or article.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    session.refresh(article)
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    return response

@router.get("/api/admin/articles/preview/{slug}", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def preview_article_endpoint(request: Request, slug: str, session: Session = Depends(get_session)):
    article = get_article_by_slug(session, slug)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            token = auth[7:]
            user = _decode_and_validate_user(token, session)
            if user.role not in ("admin", "editor") and article.author_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to preview this article")
        except HTTPException as e:
            raise e
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    session.refresh(article)
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    return response

@router.post("/api/articles/{slug}/view")
def record_view_endpoint(request: Request, slug: str, session: Session = Depends(get_session)):
    article = get_article_by_slug(session, slug)
    if not article or article.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        
    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "127.0.0.1").split(",")[0].strip()
    record_view(session, article.id, client_ip)
    session.commit()
    return {"status": "ok"}

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

@router.post("/api/admin/articles", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def create_article_endpoint(
    data: ArticleCreate,
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
):
    article = create_article(
        session,
        data.title,
        data.content,
        data.description,
        data.send_newsletter,
        data.tag_names,
        data.scheduled_for,
        author_id=user.id,
    )
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    if article.author:
        response["author"] = {"id": str(article.author.id), "email": article.author.email}
    else:
        response["author"] = None
    return response

@router.get("/api/admin/articles", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def list_admin_articles_endpoint(
    skip: int = 0,
    limit: int = 50,
    sort: str = "created_at",
    order: str = "desc",
    status_filter: str = Query(default="", alias="status"),
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
):
    from sqlmodel import select
    from sqlalchemy.orm import selectinload

    SORT_COLUMNS = {
        "title": Article.title,
        "status": Article.status,
        "published_at": Article.published_at,
        "created_at": Article.created_at,
        "updated_at": Article.updated_at,
    }

    if sort not in SORT_COLUMNS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort column: {sort}")
    if order not in ("asc", "desc"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid order: {order}")

    limit = min(limit, 200)

    sort_column = SORT_COLUMNS[sort]
    if order == "asc":
        order_clause = sort_column.asc()
    else:
        order_clause = sort_column.desc()

    stmt = select(Article).order_by(order_clause).offset(skip).limit(limit).options(selectinload(Article.tags), selectinload(Article.author))

    if user.role == "contributor":
        stmt = stmt.where(Article.author_id == user.id)

    if status_filter:
        stmt = stmt.where(Article.status == status_filter)

    articles = session.exec(stmt).all()

    result = []
    for article in articles:
        article_data = article.model_dump()
        article_data["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
        if article.author:
            article_data["author"] = {"id": str(article.author.id), "email": article.author.email}
        else:
            article_data["author"] = None

        # Include latest rejection feedback for contributors
        if user.role == "contributor":
            latest_rejection = session.exec(
                select(ReviewAction)
                .where(ReviewAction.article_id == article.id, ReviewAction.action == "rejected")
                .order_by(ReviewAction.created_at.desc())
                .limit(1)
            ).first()
            article_data["has_been_rejected"] = latest_rejection is not None
            article_data["latest_rejection_feedback"] = latest_rejection.feedback if latest_rejection else None
        result.append(article_data)
    return result

@router.get("/api/admin/articles/performance", dependencies=[Depends(require_role(["admin"]))])
def get_articles_performance_list(session: Session = Depends(get_session)):
    from app.services.article_metrics_service import get_articles_metrics_batch
    
    articles = session.exec(select(Article).order_by(Article.created_at.desc()).limit(500)).all()
    return get_articles_metrics_batch(session, articles)


@router.get("/api/admin/articles/review", dependencies=[Depends(require_role(["admin", "editor"]))])
def list_review_queue_endpoint(session: Session = Depends(get_session)):
    from sqlalchemy.orm import selectinload
    articles = session.exec(
        select(Article)
        .where(Article.status == "pending_review")
        .order_by(Article.submitted_at.desc())
        .options(selectinload(Article.tags), selectinload(Article.author))
    ).all()
    result = []
    for article in articles:
        article_data = article.model_dump()
        article_data["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
        if article.author:
            article_data["author"] = {"id": str(article.author.id), "email": article.author.email}
        else:
            article_data["author"] = None

        latest_rejection = session.exec(
            select(ReviewAction)
            .where(ReviewAction.article_id == article.id, ReviewAction.action == "rejected")
            .order_by(ReviewAction.created_at.desc())
            .limit(1)
        ).first()
        article_data["latest_rejection_feedback"] = latest_rejection.feedback if latest_rejection else None

        result.append(article_data)
    return result


@router.get("/api/admin/articles/review/count", dependencies=[Depends(require_role(["admin", "editor"]))])
def review_count_endpoint(session: Session = Depends(get_session)):
    count = session.exec(
        select(func.count(Article.id)).where(Article.status == "pending_review")
    ).first() or 0
    return {"pending_count": count}


@router.get("/api/admin/articles/{article_id}", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def get_admin_article_endpoint(
    article_id: UUID,
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
):
    from sqlalchemy.orm import selectinload
    article = session.exec(
        select(Article).where(Article.id == article_id).options(selectinload(Article.author))
    ).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if user.role == "contributor" and str(article.author_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    if article.author:
        response["author"] = {"id": str(article.author.id), "email": article.author.email}

    if user.role == "contributor":
        latest_rejection = session.exec(
            select(ReviewAction)
            .where(ReviewAction.article_id == article.id, ReviewAction.action == "rejected")
            .order_by(ReviewAction.created_at.desc())
            .limit(1)
        ).first()
        response["has_been_rejected"] = latest_rejection is not None
        response["latest_rejection_feedback"] = latest_rejection.feedback if latest_rejection else None

    return response


@router.post("/api/admin/articles/{article_id}/submit-review", dependencies=[Depends(require_role(["contributor"]))])
def submit_review_endpoint(
    article_id: UUID,
    user=Depends(require_role(["contributor"])),
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if str(article.author_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only submit your own articles for review")
    article.status = "pending_review"
    article.submitted_at = datetime.now(timezone.utc)
    article.updated_at = datetime.now(timezone.utc)
    session.add(article)
    session.commit()
    session.refresh(article)
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    if article.author:
        response["author"] = {"id": str(article.author.id), "email": article.author.email}
    return response


@router.post("/api/admin/articles/{article_id}/approve", dependencies=[Depends(require_role(["admin", "editor"]))])
def approve_review_endpoint(
    article_id: UUID,
    user=Depends(require_role(["admin", "editor"])),
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    review_action = ReviewAction(
        article_id=article.id,
        reviewer_id=user.id,
        action="approved",
    )
    article.status = "published"
    article.published_at = datetime.now(timezone.utc)
    article.submitted_at = None
    article.updated_at = datetime.now(timezone.utc)
    session.add(article)
    session.add(review_action)
    session.commit()
    session.refresh(article)
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    if article.author:
        response["author"] = {"id": str(article.author.id), "email": article.author.email}
    return response


@router.post("/api/admin/articles/{article_id}/reject", dependencies=[Depends(require_role(["admin", "editor"]))])
def reject_review_endpoint(
    article_id: UUID,
    data: ReviewRejectRequest,
    user=Depends(require_role(["admin", "editor"])),
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    review_action = ReviewAction(
        article_id=article.id,
        reviewer_id=user.id,
        action="rejected",
        feedback=data.feedback,
    )
    article.status = "draft"
    article.submitted_at = None
    article.updated_at = datetime.now(timezone.utc)
    session.add(article)
    session.add(review_action)
    session.commit()
    session.refresh(article)
    response = article.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    if article.author:
        response["author"] = {"id": str(article.author.id), "email": article.author.email}
    return response


@router.put("/api/articles/{article_id}", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
async def update_article_endpoint(
    article_id: UUID,
    data: ArticleUpdate,
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    
    # Check edit permission
    if not check_article_permission(user, article, "edit_own"):
        if not check_article_permission(user, article, "edit_others"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
    
    # Check publish permission
    if data.status == "published" and not check_article_permission(user, article, "publish"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    
    should_send_newsletter = False
    change_type = "save"
    
    if data.status == "published" and article.status == "draft":
        from datetime import datetime, timezone
        article.published_at = datetime.now(timezone.utc)
        should_send_newsletter = article.send_newsletter if data.send_newsletter is None else data.send_newsletter
        change_type = "publish"
    elif data.status == "draft" and article.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unpublish an article",
        )
    
    create_revision(session, article, change_type, author_id=user.id)
    
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
    if data.scheduled_for is not None:
        update_data["scheduled_for"] = data.scheduled_for
    
    updated = update_article(session, article, **update_data)
    
    # Serialize response before potential session commit in newsletter send
    response_data = updated.model_dump()
    response_data["tags"] = [TagRead.model_validate(t).model_dump() for t in updated.tags]
    
    if should_send_newsletter:
        await send_newsletter_for_article(arq_pool, updated, defer_until=updated.scheduled_for)
    
    return response_data

@router.delete("/api/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def delete_article_endpoint(
    article_id: UUID,
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    
    if not check_article_permission(user, article, "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    
    delete_article(session, article)
    return None

@router.post("/api/admin/articles/import", response_model=ImportResult, dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
async def import_markdown_endpoint(
    files: list[UploadFile] = File(...),
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
):
    from app.services.markdown_import_service import import_markdown_files
    file_contents = []
    for f in files:
        content = await f.read()
        file_contents.append((f.filename, content))
    return import_markdown_files(session, file_contents, author_id=user.id)

@router.post("/api/admin/articles/autosave", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def autosave_create_article_endpoint(
    data: ArticleAutoSave,
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
):
    article = create_article(
        session,
        data.title or "Untitled",
        data.content or {"type": "doc", "content": [{"type": "paragraph"}]},
        data.description,
        send_newsletter=False,
        tag_names=data.tag_names,
        scheduled_for=None,
        author_id=user.id,
    )
    response_data = article.model_dump()
    response_data["tags"] = [TagRead.model_validate(t).model_dump() for t in article.tags]
    return response_data

@router.put("/api/admin/articles/{article_id}/autosave", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def autosave_article_endpoint(
    article_id: UUID,
    data: ArticleAutoSave,
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    if not check_article_permission(user, article, "edit_own"):
        if not check_article_permission(user, article, "edit_others"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

    update_data = {}
    if data.title is not None:
        update_data["title"] = data.title
    if data.content is not None:
        update_data["content"] = data.content
    if data.description is not None:
        update_data["description"] = data.description
    if data.tag_names is not None:
        update_data["tag_names"] = data.tag_names

    # Auto-save only reverts draft/pending_review articles to draft; never touches published
    if article.status in ("draft", "pending_review"):
        update_data["status"] = "draft"
        update_data["published_at"] = None

    updated = update_article(session, article, **update_data)

    response_data = updated.model_dump()
    response_data["tags"] = [TagRead.model_validate(t).model_dump() for t in updated.tags]
    return response_data

# Tag admin endpoints

@router.get("/api/admin/tags", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def list_tags_endpoint(q: Optional[str] = None, session: Session = Depends(get_session)):
    from sqlmodel import select, func
    statement = select(Tag)
    if q:
        statement = statement.where(Tag.name.ilike(f"%{q}%"))
    tags = session.exec(statement).all()
    
    # Single query to get all article counts
    article_counts = session.exec(
        select(ArticleTag.tag_id, func.count(ArticleTag.article_id))
        .group_by(ArticleTag.tag_id)
    ).all()
    count_map = {tag_id: count for tag_id, count in article_counts}
    
    result = []
    for tag in tags:
        tag_data = TagRead.model_validate(tag).model_dump()
        tag_data["article_count"] = count_map.get(tag.id, 0)
        result.append(tag_data)
    return result

@router.delete("/api/admin/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role(["admin", "editor"]))])
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

@router.post("/api/admin/articles/{article_id}/preview-email", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def preview_email_endpoint(article_id: UUID, session: Session = Depends(get_session)):
    from app.services.email_service import send_newsletter_email, EmailServiceError
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    
    html = render_tiptap_to_email_html(article.content)
    # Use dummy unsubscribe token for preview
    try:
        send_newsletter_email(settings.ADMIN_EMAIL, article.title, html, "preview-mode-no-unsubscribe")
    except EmailServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send preview email: {str(e)}"
        )
    return {"message": "Preview sent successfully"}

@router.get("/api/admin/articles/{article_id}/revisions", response_model=list[RevisionListRead], dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def list_article_revisions_endpoint(article_id: UUID, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    revisions = list_revisions(session, article_id)
    result = []
    for rev in revisions:
        rev_data = RevisionListRead.model_validate(rev).model_dump()
        rev_data["author_email"] = rev.author.email if rev.author else None
        result.append(rev_data)
    return result

@router.get("/api/admin/articles/{article_id}/revisions/{version_number}", response_model=RevisionRead, dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def get_article_revision_endpoint(article_id: UUID, version_number: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    revision = get_revision(session, article_id, version_number)
    if not revision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision not found")
    rev_data = RevisionRead.model_validate(revision).model_dump()
    rev_data["author_email"] = revision.author.email if revision.author else None
    return rev_data

@router.post("/api/admin/articles/{article_id}/revisions/{version_number}/restore", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def restore_article_revision_endpoint(
    article_id: UUID,
    version_number: int,
    user=Depends(require_role(["admin", "editor", "contributor"])),
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    restored = restore_revision(session, article, version_number, author_id=user.id)
    if not restored:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision not found")
    response = restored.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in restored.tags]
    return response

@router.put("/api/admin/articles/{article_id}/reassign", dependencies=[Depends(require_role(["admin"]))])
def reassign_article_endpoint(
    article_id: UUID,
    data: ArticleReassignRequest,
    user=Depends(require_role(["admin"])),
    session: Session = Depends(get_session),
):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    try:
        new_author_id = uuid.UUID(data.author_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid author_id format")

    try:
        updated = reassign_article(session, article, new_author_id, actor_id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response = updated.model_dump()
    response["tags"] = [TagRead.model_validate(t).model_dump() for t in updated.tags]
    if updated.author:
        response["author"] = {"id": str(updated.author.id), "email": updated.author.email}
    else:
        response["author"] = None
    return response

@router.get("/api/admin/newsletter-blasts/{article_id}/status", dependencies=[Depends(require_role(["admin"]))])
def get_newsletter_blast_status_endpoint(article_id: UUID, session: Session = Depends(get_session)):
    from sqlmodel import func, select
    
    # Counts of pending, sent, failed
    counts = session.exec(
        select(NewsletterSend.status, func.count(NewsletterSend.id))
        .where(NewsletterSend.article_id == article_id)
        .group_by(NewsletterSend.status)
    ).all()
    
    results = {
        "pending": 0,
        "sent": 0,
        "failed": 0,
        "total": 0,
        "progress_percentage": 0.0
    }
    
    for status_name, count in counts:
        if status_name in results:
            results[status_name] = count
        results["total"] += count
        
    if results["total"] > 0:
        # Progress is (sent + failed) / total
        completed = results["sent"] + results["failed"]
        results["progress_percentage"] = (completed / results["total"]) * 100
        
    return results

@router.get("/api/admin/templates/preview/{template_name}", dependencies=[Depends(require_role(["admin", "editor", "contributor"]))])
def preview_template_endpoint(template_name: str):
    from app.services.email_renderer import render
    from app.config import settings
    
    mock_context = {
        "preview_text": f"{template_name.capitalize()} Preview",
    }
    
    if template_name == "newsletter":
        mock_context.update({
            "article_title": "Interstellar Travel: The Next Frontier",
            "article_html": """
                <p>Welcome to the future of space exploration. As we look towards the stars, the possibilities are infinite.</p>
                <h2>Propulsion Systems</h2>
                <p>New ion engines are allowing us to reach speeds never before possible. 
                   <a href="#">Read more about the tech here</a>.</p>
                <img src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=600" alt="Space" width="600" />
                <blockquote>"The stars are not the limit, they are just the beginning." - Commander Shepard</blockquote>
                <ul>
                    <li>Deep space longevity</li>
                    <li>Radiation shielding</li>
                    <li>Cryogenic sleep pods</li>
                </ul>
            """,
            "unsubscribe_url": "#",
        })
    elif template_name == "confirmation":
        mock_context.update({
            "confirmation_url": "#",
        })
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        
    try:
        html = render(f"{template_name}.mjml", mock_context)
        return Response(content=html, media_type="text/html")
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Template preview error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
