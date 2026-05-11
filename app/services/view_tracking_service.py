import hashlib
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from app.models.article_view import ArticleView

def record_view(session: Session, article_id, ip_address: str) -> None:
    """Record a view for an article, deduplicating by IP hash within 24 hours."""
    ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    existing = session.exec(
        select(ArticleView)
        .where(ArticleView.article_id == article_id)
        .where(ArticleView.ip_hash == ip_hash)
        .where(ArticleView.viewed_at >= cutoff)
    ).first()

    if existing:
        return

    view = ArticleView(
        article_id=article_id,
        ip_hash=ip_hash,
    )
    session.add(view)
