from sqlmodel import Session, select
from app.models.article import Article
from app.models.subscriber import Subscriber
from app.models.newsletter_send import NewsletterSend
from app.services.subscriber_service import list_active_subscribers
from app.services.email_service import send_newsletter_email
from app.services.tiptap_renderer import render_tiptap_to_email_html

def send_newsletter_for_article(session: Session, article: Article) -> None:
    """Send newsletter to all active subscribers who haven't received it yet."""
    subscribers = list_active_subscribers(session)
    
    article_html = render_tiptap_to_email_html(article.content)
    
    for subscriber in subscribers:
        # Check if already sent
        already_sent = session.exec(
            select(NewsletterSend).where(
                NewsletterSend.article_id == article.id,
                NewsletterSend.subscriber_id == subscriber.id,
            )
        ).first()
        
        if already_sent:
            continue
        
        send_newsletter_email(
            subscriber.email,
            article.title,
            article_html,
            subscriber.confirmation_token,
        )
        
        send_record = NewsletterSend(
            article_id=article.id,
            subscriber_id=subscriber.id,
        )
        session.add(send_record)
    
    session.commit()
