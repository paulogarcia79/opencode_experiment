from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func
from app.database import get_session
from app.dependencies import require_admin
from app.models import Subscriber, NewsletterSend, Article, ArticleView
from app.models.newsletter_send import NewsletterSend as NS
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from uuid import UUID

router = APIRouter(prefix="/api/admin/analytics", tags=["analytics"])

@router.get("", dependencies=[Depends(require_admin)])
def get_analytics(
    range: str = Query("30d", pattern="^(7d|30d|90d)$"),
    session: Session = Depends(get_session)
):
    days = int(range.replace("d", ""))
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    # 1. Summary
    total_active = session.exec(select(func.count(Subscriber.id)).where(Subscriber.status == "active")).first() or 0
    total_pending = session.exec(select(func.count(Subscriber.id)).where(Subscriber.status == "pending")).first() or 0
    total_unsubscribed = session.exec(select(func.count(Subscriber.id)).where(Subscriber.status == "unsubscribed")).first() or 0
    
    # 2. Growth (Signups and Unsubscribes by date)
    # SQLite uses strftime, PostgreSQL uses date_trunc. 
    # For now, let's use a simple approach that works for both if possible or detect dialect
    
    dialect = session.bind.dialect.name
    if dialect == "sqlite":
        date_func = func.strftime('%Y-%m-%d', Subscriber.created_at)
        unsub_date_func = func.strftime('%Y-%m-%d', Subscriber.updated_at)
        date_func_ns = func.strftime('%Y-%m-%d', NewsletterSend.created_at)
    else:
        date_func = func.date_trunc('day', Subscriber.created_at)
        unsub_date_func = func.date_trunc('day', Subscriber.updated_at)
        date_func_ns = func.date_trunc('day', NewsletterSend.created_at)

    signups = session.exec(
        select(date_func, func.count(Subscriber.id))
        .where(Subscriber.created_at >= start_date)
        .group_by(date_func)
    ).all()

    unsubscribes = session.exec(
        select(unsub_date_func, func.count(Subscriber.id))
        .where(Subscriber.status == "unsubscribed")
        .where(Subscriber.updated_at >= start_date)
        .group_by(unsub_date_func)
    ).all()

    # Engagement time-series
    opens_ts = session.exec(
        select(date_func_ns, func.sum(NewsletterSend.open_count))
        .where(NewsletterSend.created_at >= start_date)
        .group_by(date_func_ns)
    ).all()

    clicks_ts = session.exec(
        select(date_func_ns, func.sum(NewsletterSend.click_count))
        .where(NewsletterSend.created_at >= start_date)
        .group_by(date_func_ns)
    ).all()

    # 3. Delivery Stats
    delivery_stats = session.exec(
        select(NewsletterSend.status, func.count(NewsletterSend.id))
        .where(NewsletterSend.created_at >= start_date)
        .group_by(NewsletterSend.status)
    ).all()

    delivery_results = {s: c for s, c in delivery_stats}
    total_sent = delivery_results.get("sent", 0)

    # 4. Engagement Stats
    total_opens = session.exec(
        select(func.sum(NewsletterSend.open_count))
        .where(NewsletterSend.created_at >= start_date)
    ).first() or 0

    total_clicks = session.exec(
        select(func.sum(NewsletterSend.click_count))
        .where(NewsletterSend.created_at >= start_date)
    ).first() or 0

    open_rate = (total_opens / total_sent * 100) if total_sent > 0 else 0
    ctr = (total_clicks / total_sent * 100) if total_sent > 0 else 0

    # 5. Bounce & Complaint Stats
    total_bounces = session.exec(
        select(func.count(NewsletterSend.id))
        .where(NewsletterSend.created_at >= start_date)
        .where(NewsletterSend.status == "failed")
        .where(NewsletterSend.error_message.like("Bounced%"))
    ).first() or 0

    total_complaints = session.exec(
        select(func.count(NewsletterSend.id))
        .where(NewsletterSend.created_at >= start_date)
        .where(NewsletterSend.status == "failed")
        .where(NewsletterSend.error_message == "Complained")
    ).first() or 0

    bounce_rate = (total_bounces / total_sent * 100) if total_sent > 0 else 0
    complaint_rate = (total_complaints / total_sent * 100) if total_sent > 0 else 0

    # Bounce & Complaint time-series
    bounces_ts = session.exec(
        select(date_func_ns, func.count(NewsletterSend.id))
        .where(NewsletterSend.created_at >= start_date)
        .where(NewsletterSend.status == "failed")
        .where(NewsletterSend.error_message.like("Bounced%"))
        .group_by(date_func_ns)
    ).all()

    complaints_ts = session.exec(
        select(date_func_ns, func.count(NewsletterSend.id))
        .where(NewsletterSend.created_at >= start_date)
        .where(NewsletterSend.status == "failed")
        .where(NewsletterSend.error_message == "Complained")
        .group_by(date_func_ns)
    ).all()

    return {
        "summary": {
            "total_active": total_active,
            "total_pending": total_pending,
            "total_unsubscribed": total_unsubscribed,
            "total_opens": int(total_opens),
            "total_clicks": int(total_clicks),
            "total_bounces": int(total_bounces),
            "total_complaints": int(total_complaints),
            "open_rate": round(open_rate, 2),
            "ctr": round(ctr, 2),
            "bounce_rate": round(bounce_rate, 2),
            "complaint_rate": round(complaint_rate, 2),
        },
        "growth": {
            "signups": [{"date": d, "count": c} for d, c in signups],
            "unsubscribes": [{"date": d, "count": c} for d, c in unsubscribes],
            "opens": [{"date": d, "count": int(c or 0)} for d, c in opens_ts],
            "clicks": [{"date": d, "count": int(c or 0)} for d, c in clicks_ts],
            "bounces": [{"date": d, "count": c} for d, c in bounces_ts],
            "complaints": [{"date": d, "count": c} for d, c in complaints_ts],
        },
        "delivery": {
            "sent": delivery_results.get("sent", 0),
            "failed": delivery_results.get("failed", 0),
            "pending": delivery_results.get("pending", 0),
        }
    }

article_analytics_router = APIRouter(prefix="/api/admin/articles/{article_id}/analytics", tags=["article-analytics"])

@article_analytics_router.get("", dependencies=[Depends(require_admin)])
def get_article_analytics(article_id: UUID, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    total_views = session.exec(
        select(func.count(ArticleView.id)).where(ArticleView.article_id == article_id)
    ).first() or 0

    unique_views_24h = session.exec(
        select(func.count(func.distinct(ArticleView.ip_hash)))
        .where(ArticleView.article_id == article_id)
        .where(ArticleView.viewed_at >= datetime.now(timezone.utc) - timedelta(days=1))
    ).first() or 0

    email_sent = session.exec(
        select(func.count(NS.id))
        .where(NS.article_id == article_id)
        .where(NS.status == "sent")
    ).first() or 0

    total_opens = session.exec(
        select(func.sum(NS.open_count))
        .where(NS.article_id == article_id)
    ).first() or 0

    total_clicks = session.exec(
        select(func.sum(NS.click_count))
        .where(NS.article_id == article_id)
    ).first() or 0

    open_rate = (int(total_opens) / email_sent * 100) if email_sent > 0 else 0
    ctr = (int(total_clicks) / email_sent * 100) if email_sent > 0 else 0

    return {
        "total_views": total_views,
        "unique_views_24h": unique_views_24h,
        "email_sent": email_sent,
        "email_opens": int(total_opens),
        "email_clicks": int(total_clicks),
        "email_open_rate": round(open_rate, 2),
        "email_ctr": round(ctr, 2),
    }

@article_analytics_router.get("/performance", dependencies=[Depends(require_admin)])
def get_articles_performance_list(session: Session = Depends(get_session)):
    articles = session.exec(select(Article)).all()

    results = []
    for article in articles:
        total_views = session.exec(
            select(func.count(ArticleView.id)).where(ArticleView.article_id == article.id)
        ).first() or 0

        unique_views_24h = session.exec(
            select(func.count(func.distinct(ArticleView.ip_hash)))
            .where(ArticleView.article_id == article.id)
            .where(ArticleView.viewed_at >= datetime.now(timezone.utc) - timedelta(days=1))
        ).first() or 0

        email_sent = session.exec(
            select(func.count(NS.id))
            .where(NS.article_id == article.id)
            .where(NS.status == "sent")
        ).first() or 0

        total_opens = session.exec(
            select(func.sum(NS.open_count))
            .where(NS.article_id == article.id)
        ).first() or 0

        total_clicks = session.exec(
            select(func.sum(NS.click_count))
            .where(NS.article_id == article.id)
        ).first() or 0

        open_rate = (int(total_opens) / email_sent * 100) if email_sent > 0 else 0
        ctr = (int(total_clicks) / email_sent * 100) if email_sent > 0 else 0

        results.append({
            "id": str(article.id),
            "title": article.title,
            "slug": article.slug,
            "status": article.status,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "total_views": total_views,
            "unique_views_24h": unique_views_24h,
            "email_sent": email_sent,
            "email_opens": int(total_opens),
            "email_clicks": int(total_clicks),
            "email_open_rate": round(open_rate, 2),
            "email_ctr": round(ctr, 2),
        })

    return results
