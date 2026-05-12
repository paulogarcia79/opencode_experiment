from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select, func
from app.models import Article, ArticleView
from app.models.newsletter_send import NewsletterSend as NS


def get_article_metrics(session: Session, article_id) -> dict:
    """Get all metrics for a single article in optimized queries."""
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


def get_articles_metrics_batch(session: Session, articles: list[Article]) -> list[dict]:
    """Get metrics for multiple articles using batched queries."""
    if not articles:
        return []

    article_ids = [a.id for a in articles]

    # Batch view counts
    view_counts = session.exec(
        select(ArticleView.article_id, func.count(ArticleView.id))
        .where(ArticleView.article_id.in_(article_ids))
        .group_by(ArticleView.article_id)
    ).all()
    view_count_map = {aid: count for aid, count in view_counts}

    # Batch unique views 24h
    unique_views_24h = session.exec(
        select(ArticleView.article_id, func.count(func.distinct(ArticleView.ip_hash)))
        .where(ArticleView.article_id.in_(article_ids))
        .where(ArticleView.viewed_at >= datetime.now(timezone.utc) - timedelta(days=1))
        .group_by(ArticleView.article_id)
    ).all()
    unique_views_map = {aid: count for aid, count in unique_views_24h}

    # Batch email sent counts
    email_sent_counts = session.exec(
        select(NS.article_id, func.count(NS.id))
        .where(NS.article_id.in_(article_ids))
        .where(NS.status == "sent")
        .group_by(NS.article_id)
    ).all()
    email_sent_map = {aid: count for aid, count in email_sent_counts}

    # Batch email opens
    email_opens = session.exec(
        select(NS.article_id, func.sum(NS.open_count))
        .where(NS.article_id.in_(article_ids))
        .group_by(NS.article_id)
    ).all()
    email_opens_map = {aid: (total or 0) for aid, total in email_opens}

    # Batch email clicks
    email_clicks = session.exec(
        select(NS.article_id, func.sum(NS.click_count))
        .where(NS.article_id.in_(article_ids))
        .group_by(NS.article_id)
    ).all()
    email_clicks_map = {aid: (total or 0) for aid, total in email_clicks}

    results = []
    for article in articles:
        aid = article.id
        email_sent = email_sent_map.get(aid, 0)
        total_opens = email_opens_map.get(aid, 0)
        total_clicks = email_clicks_map.get(aid, 0)
        open_rate = (total_opens / email_sent * 100) if email_sent > 0 else 0
        ctr = (total_clicks / email_sent * 100) if email_sent > 0 else 0

        results.append({
            "id": str(aid),
            "title": article.title,
            "slug": article.slug,
            "status": article.status,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "total_views": view_count_map.get(aid, 0),
            "unique_views_24h": unique_views_map.get(aid, 0),
            "email_sent": email_sent,
            "email_opens": total_opens,
            "email_clicks": total_clicks,
            "email_open_rate": round(open_rate, 2),
            "email_ctr": round(ctr, 2),
        })

    return results
