from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from app.database import get_session
from app.models.email_event import EmailEvent
from app.models.newsletter_send import NewsletterSend
from datetime import datetime
import logging

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

@router.post("/resend")
async def resend_webhook(request: Request, session: Session = Depends(get_session)):
    payload = await request.json()
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
        
        # We'll use tags or headers to find our newsletter_send_id
        # For now, let's assume we pass it in 'tags'
        tags = data.get("tags", {})
        send_id_str = tags.get("newsletter_send_id")
        
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
                timestamp=datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.utcnow(),
                raw_payload=event
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
                    send_record.error_message = "Bounced"
                
                session.add(send_record)
                
        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            continue

    session.commit()
    return {"status": "ok"}
