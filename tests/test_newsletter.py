from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from app.config import settings
from app.models.article import Article
from app.models.subscriber import Subscriber
from app.services.newsletter_service import send_newsletter_for_article
from app.services.subscriber_service import create_subscriber, confirm_subscriber
from app.services.article_service import create_article


def test_newsletter_renders_images_with_absolute_urls(session):
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
    subscriber = create_subscriber(session, "newsletter-test@example.com")
    confirm_subscriber(session, subscriber.confirmation_token)

    session.commit()

    # Mock the email service to capture sent HTML
    sent_html = None
    def capture_email(email, title, html, token):
        nonlocal sent_html
        sent_html = html

    with patch('app.services.newsletter_service.send_newsletter_email', side_effect=capture_email):
        send_newsletter_for_article(session, article)

    # Verify newsletter HTML contains absolute URLs
    assert sent_html is not None
    assert f"{settings.APP_BASE_URL}/uploads/2025/05/photo.png" in sent_html
    assert 'src="https://external.com/img.jpg"' in sent_html
    assert 'style="max-width:100%;height:auto;display:block;"' in sent_html
    assert "Check out this image" in sent_html


def test_newsletter_skips_already_sent(session):
    """Newsletter should not send to subscribers who already received the article."""
    article = create_article(session, "Already Sent", {"type": "doc", "content": []})
    article.status = "published"
    article.published_at = datetime.now(timezone.utc)
    session.add(article)

    subscriber = create_subscriber(session, "already-sent@example.com")
    confirm_subscriber(session, subscriber.confirmation_token)
    session.commit()

    # First send
    with patch('app.services.newsletter_service.send_newsletter_email') as mock_send:
        send_newsletter_for_article(session, article)
        assert mock_send.call_count == 1

    # Second send should skip
    with patch('app.services.newsletter_service.send_newsletter_email') as mock_send:
        send_newsletter_for_article(session, article)
        assert mock_send.call_count == 0
