from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from app.database import get_session
from app.dependencies import require_admin
from app.models import Subscriber, NewsletterSend
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

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
    else:
        date_func = func.date_trunc('day', Subscriber.created_at)
        unsub_date_func = func.date_trunc('day', Subscriber.updated_at)

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

    # 3. Delivery Stats
    delivery_stats = session.exec(
        select(NewsletterSend.status, func.count(NewsletterSend.id))
        .where(NewsletterSend.created_at >= start_date)
        .group_by(NewsletterSend.status)
    ).all()

    delivery_results = {s: c for s, c in delivery_stats}

    return {
        "summary": {
            "total_active": total_active,
            "total_pending": total_pending,
            "total_unsubscribed": total_unsubscribed,
        },
        "growth": {
            "signups": [{"date": d, "count": c} for d, c in signups],
            "unsubscribes": [{"date": d, "count": c} for d, c in unsubscribes],
        },
        "delivery": {
            "sent": delivery_results.get("sent", 0),
            "failed": delivery_results.get("failed", 0),
            "pending": delivery_results.get("pending", 0),
        }
    }
