from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from app.database import get_session
from app.models.email_event import EmailEvent
from app.models.newsletter_send import NewsletterSend
from app.models.subscriber import Subscriber
from app.config import settings
from datetime import datetime, timezone
import logging

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

def _verify_svix_signature(request: Request, raw_body: bytes) -> bool:
    """Verify Svix webhook signature. Returns True if valid or secret not configured."""
    secret = settings.RESEND_WEBHOOK_SECRET
    if not secret:
        logger.warning("RESEND_WEBHOOK_SECRET not configured - skipping signature verification")
        return True
    
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")
    
    if not all([svix_id, svix_timestamp, svix_signature]):
        return False
    
    try:
        from svix.webhooks import Webhook
        webhook = Webhook(secret)
        webhook.verify(raw_body, request.headers)
        return True
    except Exception as e:
        logger.error(f"Svix signature verification failed: {e}")
        return False

@router.post("/resend")
async def resend_webhook(request: Request, session: Session = Depends(get_session)):
    raw_body = await request.body()
    payload = await request.json()
    
    if not _verify_svix_signature(request, raw_body):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    logger.info(f"Received Resend webhook: {payload}")
    
    # Resend sends an array of events or a single event depending on configuration
    if isinstance(payload, dict):
        events = [payload]
    else:
        events = payload

    for event in events:
        event_type = event.get("type")
        created_at_str = event.get("created_at")
        data = event.get("data", {})
        svix_id = event.get("svix_id")
        
        # Check for duplicate event via svix_id
        if svix_id:
            existing = session.exec(select(EmailEvent).where(EmailEvent.svix_id == svix_id)).first()
            if existing:
                logger.info(f"Skipping duplicate event: {svix_id}")
                continue
        
        # Resend sends tags as a list of {name, value} objects
        tags_list = data.get("tags", [])
        send_id_str = None
        if isinstance(tags_list, list):
            for tag in tags_list:
                if isinstance(tag, dict) and tag.get("name") == "newsletter_send_id":
                    send_id_str = tag.get("value")
                    break
        elif isinstance(tags_list, dict):
            # Fallback for dict format
            send_id_str = tags_list.get("newsletter_send_id")
        
        if not send_id_str:
            # Fallback: check metadata or other fields if needed
            continue
            
        try:
            import uuid
            send_id = uuid.UUID(send_id_str)
            
            # Log the raw event
            email_event = EmailEvent(
                newsletter_send_id=send_id,
                event_type=event_type,
                timestamp=datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.now(timezone.utc),
                raw_payload=event,
                svix_id=svix_id,
            )
            session.add(email_event)
            
            # Update NewsletterSend metrics
            send_record = session.get(NewsletterSend, send_id)
            if send_record:
                if event_type == "email.opened":
                    send_record.open_count += 1
                    if not send_record.opened_at:
                        send_record.opened_at = email_event.timestamp
                elif event_type == "email.clicked":
                    send_record.click_count += 1
                    if not send_record.clicked_at:
                        send_record.clicked_at = email_event.timestamp
                elif event_type == "email.bounced":
                    send_record.status = "failed"
                    bounce_info = data.get("bounce", {})
                    bounce_type = bounce_info.get("type", "Unknown")
                    bounce_message = bounce_info.get("message", "Bounced")
                    send_record.error_message = f"Bounced ({bounce_type}): {bounce_message}"
                    
                    # Unsubscribe on permanent bounce
                    if bounce_type == "Permanent":
                        recipient_emails = data.get("to", [])
                        for email_addr in recipient_emails:
                            sub = session.exec(select(Subscriber).where(Subscriber.email == email_addr)).first()
                            if sub and sub.status != "unsubscribed":
                                sub.status = "unsubscribed"
                                session.add(sub)
                                logger.info(f"Unsubscribed {email_addr} due to permanent bounce")
                elif event_type == "email.complained":
                    send_record.status = "failed"
                    send_record.error_message = "Complained"
                    
                    # Unsubscribe on complaint
                    recipient_emails = data.get("to", [])
                    for email_addr in recipient_emails:
                        sub = session.exec(select(Subscriber).where(Subscriber.email == email_addr)).first()
                        if sub and sub.status != "unsubscribed":
                            sub.status = "unsubscribed"
                            session.add(sub)
                            logger.info(f"Unsubscribed {email_addr} due to complaint")
                
                session.add(send_record)
                
        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            continue

    session.commit()
    return {"status": "ok"}
