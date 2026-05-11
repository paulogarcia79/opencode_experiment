from app.redis import get_redis_settings
from app.services.email_service import send_confirmation_email, send_newsletter_email, EmailServiceError
from app.services.tiptap_renderer import render_tiptap_to_email_html
from app.database import get_session
from app.models.subscriber import Subscriber
from app.models.newsletter_send import NewsletterSend
from app.models.article import Article
from sqlmodel import select
import uuid
import logging

logger = logging.getLogger(__name__)

async def send_confirmation_email_task(ctx, email: str, token: str):
    send_confirmation_email(email, token)

async def blast_newsletter_task(ctx, article_id: str, session=None):
    """Orchestrator: Create pending records and enqueue individual sends."""
    article_uuid = uuid.UUID(article_id)
    arq_pool = ctx["redis"]
    
    if session:
        await _run_blast(session, article_uuid, arq_pool)
    else:
        for session in get_session():
            await _run_blast(session, article_uuid, arq_pool)
            break

async def _run_blast(session, article_uuid, arq_pool):
    # 1. Get all active subscribers
    subscribers = session.exec(select(Subscriber).where(Subscriber.status == "active")).all()
    
    # 2. Create pending NewsletterSend records
    for subscriber in subscribers:
        # Check if already exists (idempotency)
        existing = session.exec(
            select(NewsletterSend).where(
                NewsletterSend.article_id == article_uuid,
                NewsletterSend.subscriber_id == subscriber.id
            )
        ).first()
        
        if existing:
            continue
            
        send_record = NewsletterSend(
            article_id=article_uuid,
            subscriber_id=subscriber.id,
            status="pending"
        )
        session.add(send_record)
        session.commit()
        session.refresh(send_record)
        
        # 3. Enqueue individual send
        await arq_pool.enqueue_job("send_single_email_task", send_record.id)

async def send_single_email_task(ctx, send_id: uuid.UUID, session=None):
    """Worker task to send one email."""
    if session:
        await _run_single_send(session, send_id)
    else:
        for session in get_session():
            await _run_single_send(session, send_id)
            break

async def _run_single_send(session, send_id):
    send_record = session.get(NewsletterSend, send_id)
    if not send_record or send_record.status == "sent":
        return

    article = session.get(Article, send_record.article_id)
    subscriber = session.get(Subscriber, send_record.subscriber_id)
    
    if not article or not subscriber:
        send_record.status = "failed"
        send_record.error_message = "Article or Subscriber not found"
        session.add(send_record)
        session.commit()
        return

    html = render_tiptap_to_email_html(article.content)
    
    try:
        send_newsletter_email(
            subscriber.email,
            article.title,
            html,
            subscriber.confirmation_token
        )
        send_record.status = "sent"
        session.add(send_record)
        session.commit()
    except EmailServiceError as e:
        # Check for permanent errors (domain verification, etc)
        error_str = str(e)
        is_permanent = "not verified" in error_str.lower() or "forbidden" in error_str.lower()
        
        if is_permanent:
            send_record.status = "failed"
            send_record.error_message = error_str
            session.add(send_record)
            session.commit()
        else:
            # Re-raise for ARQ to retry if transient
            raise e
    except Exception as e:
        # Catch-all for other transient errors
        logger.error(f"Unexpected error sending email {send_id}: {str(e)}")
        raise e

async def startup(ctx):
    pass

async def shutdown(ctx):
    pass

class WorkerSettings:
    functions = [send_confirmation_email_task, blast_newsletter_task, send_single_email_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = get_redis_settings()

settings = WorkerSettings
