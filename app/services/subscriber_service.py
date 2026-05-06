import secrets
from typing import Optional
from sqlmodel import Session, select
from app.models.subscriber import Subscriber
from app.services.email_service import send_confirmation_email

def create_subscriber(session: Session, email: str) -> Optional[Subscriber]:
    """Create a new pending subscriber or return existing active/pending one."""
    existing = session.exec(
        select(Subscriber).where(Subscriber.email == email)
    ).first()
    
    if existing and existing.status in ("pending", "active"):
        return existing
    
    if existing and existing.status == "unsubscribed":
        existing.status = "pending"
        existing.confirmation_token = secrets.token_urlsafe(32)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        send_confirmation_email(existing.email, existing.confirmation_token)
        return existing
    
    token = secrets.token_urlsafe(32)
    subscriber = Subscriber(
        email=email,
        status="pending",
        confirmation_token=token,
    )
    session.add(subscriber)
    session.commit()
    session.refresh(subscriber)
    send_confirmation_email(subscriber.email, subscriber.confirmation_token)
    return subscriber

def confirm_subscriber(session: Session, token: str) -> Optional[Subscriber]:
    subscriber = session.exec(
        select(Subscriber).where(
            Subscriber.confirmation_token == token,
            Subscriber.status == "pending",
        )
    ).first()
    
    if not subscriber:
        return None
    
    subscriber.status = "active"
    session.add(subscriber)
    session.commit()
    session.refresh(subscriber)
    return subscriber

def unsubscribe_subscriber(session: Session, token: str) -> Optional[Subscriber]:
    subscriber = session.exec(
        select(Subscriber).where(Subscriber.confirmation_token == token)
    ).first()
    
    if not subscriber:
        return None
    
    subscriber.status = "unsubscribed"
    session.add(subscriber)
    session.commit()
    session.refresh(subscriber)
    return subscriber

def list_active_subscribers(session: Session) -> list[Subscriber]:
    return session.exec(
        select(Subscriber).where(Subscriber.status == "active")
    ).all()
