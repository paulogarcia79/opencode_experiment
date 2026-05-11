import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from app.config import settings
from app.models.article import Article
from app.models.subscriber import Subscriber
from app.services.newsletter_service import send_newsletter_for_article
from app.services.subscriber_service import create_subscriber, confirm_subscriber
from app.services.article_service import create_article

@pytest.mark.asyncio
async def test_newsletter_renders_images_with_absolute_urls(session, arq_pool):
    """Integration test: publishing an article with images generates newsletter HTML with absolute URLs."""
    # Create article with images
    article = create_article(
        session,
        "Article with Images",
        {
            "type": "doc",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Check out this image:"}]},
                {"type": "image", "attrs": {"src": "/uploads/2025/05/photo.png", "alt": "A photo"}},
                {"type": "image", "attrs": {"src": "https://external.com/img.jpg", "alt": "External"}},
            ],
        },
    )
    article.status = "published"
    article.published_at = datetime.now(timezone.utc)
    session.add(article)

    # Create and confirm subscriber
    subscriber = await create_subscriber(session, "newsletter-test@example.com", arq_pool)
    confirm_subscriber(session, subscriber.confirmation_token)

    session.commit()

    # Mock the email service to capture sent HTML
    # We now test through the worker/service boundary
    from app.worker import send_single_email_task
    from app.models.newsletter_send import NewsletterSend
    
    send_record = NewsletterSend(article_id=article.id, subscriber_id=subscriber.id, status="pending")
    session.add(send_record)
    session.commit()

    sent_html = None
    def capture_email(email, title, html, token):
        nonlocal sent_html
        sent_html = html

    with patch('app.worker.send_newsletter_email', side_effect=capture_email):
        await send_single_email_task({}, send_record.id, session=session)

    # Verify newsletter HTML contains absolute URLs
    assert sent_html is not None
    assert f"{settings.APP_BASE_URL.rstrip('/')}/uploads/2025/05/photo.png" in sent_html
    assert 'src="https://external.com/img.jpg"' in sent_html
    assert "Check out this image" in sent_html


@pytest.mark.asyncio
async def test_newsletter_skips_already_sent(session, arq_pool):
    """Newsletter should not send to subscribers who already received the article."""
    article = create_article(session, "Already Sent", {"type": "doc", "content": []})
    article.status = "published"
    article.published_at = datetime.now(timezone.utc)
    session.add(article)

    subscriber = await create_subscriber(session, "already-sent@example.com", arq_pool)
    confirm_subscriber(session, subscriber.confirmation_token)
    session.commit()
    
    from app.worker import blast_newsletter_task
    from app.models.newsletter_send import NewsletterSend

    # First send: should enqueue jobs
    arq_pool.enqueue_job.reset_mock()
    await blast_newsletter_task({"redis": arq_pool}, str(article.id), session=session)
    assert arq_pool.enqueue_job.call_count == 1
    
    # Second send should skip because records already exist in DB
    arq_pool.enqueue_job.reset_mock()
    await blast_newsletter_task({"redis": arq_pool}, str(article.id), session=session)
    assert arq_pool.enqueue_job.call_count == 0
