import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.worker import blast_newsletter_task
from app.models.article import Article
from app.models.subscriber import Subscriber
from app.models.newsletter_send import NewsletterSend
from sqlmodel import select

@pytest.mark.asyncio
async def test_blast_newsletter_task_enqueues_individual_jobs(session, arq_pool):
    # Setup: Article and 2 subscribers
    article = Article(title="Test", content={"type": "doc", "content": []}, slug="test")
    session.add(article)
    
    sub1 = Subscriber(email="sub1@example.com", status="active", confirmation_token="token1")
    sub2 = Subscriber(email="sub2@example.com", status="active", confirmation_token="token2")
    sub3 = Subscriber(email="sub3@example.com", status="pending", confirmation_token="token3") # Should be ignored
    session.add_all([sub1, sub2, sub3])
    session.commit()
    
    # Run task
    await blast_newsletter_task({"redis": arq_pool}, str(article.id), session=session)
    
    # Verify NewsletterSend records created
    sends = session.exec(select(NewsletterSend).where(NewsletterSend.article_id == article.id)).all()
    assert len(sends) == 2
    for s in sends:
        assert s.status == "pending"
    
    # Verify jobs enqueued
    assert arq_pool.enqueue_job.call_count == 2
    arq_pool.enqueue_job.assert_any_call("send_single_email_task", sends[0].id)
    arq_pool.enqueue_job.assert_any_call("send_single_email_task", sends[1].id)

@pytest.mark.asyncio
async def test_send_single_email_task_success(session):
    from app.worker import send_single_email_task
    from app.models.newsletter_send import NewsletterSend
    
    # Setup
    article = Article(title="Hello", content={"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "World"}]}]}, slug="hello")
    sub = Subscriber(email="sub@example.com", status="active", confirmation_token="token")
    session.add_all([article, sub])
    session.commit()
    
    send_record = NewsletterSend(article_id=article.id, subscriber_id=sub.id, status="pending")
    session.add(send_record)
    session.commit()
    
    with patch("app.worker.send_newsletter_email") as mock_email:
        await send_single_email_task({}, send_record.id, session=session)
        
        mock_email.assert_called_once()
        assert mock_email.call_args[0][0] == "sub@example.com"
        assert mock_email.call_args[0][1] == "Hello"
        assert "World" in mock_email.call_args[0][2]
        
        session.refresh(send_record)
        assert send_record.status == "sent"

@pytest.mark.asyncio
async def test_send_single_email_task_permanent_failure(session):
    from app.worker import send_single_email_task
    from app.services.email_service import EmailServiceError
    
    # Setup
    article = Article(title="H", content={"type":"doc"}, slug="h")
    sub = Subscriber(email="s@ex.com", status="active", confirmation_token="t")
    session.add_all([article, sub])
    session.commit()
    
    send_record = NewsletterSend(article_id=article.id, subscriber_id=sub.id, status="pending")
    session.add(send_record)
    session.commit()
    
    with patch("app.worker.send_newsletter_email", side_effect=EmailServiceError("Domain not verified")):
        await send_single_email_task({}, send_record.id, session=session)
        
        session.refresh(send_record)
        assert send_record.status == "failed"
        assert "not verified" in send_record.error_message

@pytest.mark.asyncio
async def test_send_single_email_task_transient_failure(session):
    from app.worker import send_single_email_task
    from app.services.email_service import EmailServiceError
    
    # Setup
    article = Article(title="H", content={"type":"doc"}, slug="h2")
    sub = Subscriber(email="s2@ex.com", status="active", confirmation_token="t2")
    session.add_all([article, sub])
    session.commit()
    
    send_record = NewsletterSend(article_id=article.id, subscriber_id=sub.id, status="pending")
    session.add(send_record)
    session.commit()
    
    with patch("app.worker.send_newsletter_email", side_effect=EmailServiceError("Rate limit exceeded")):
        with pytest.raises(EmailServiceError):
            await send_single_email_task({}, send_record.id, session=session)
        
        session.refresh(send_record)
        assert send_record.status == "pending" # Should not be updated to failed yet

@pytest.mark.asyncio
async def test_publish_article_enqueues_blast(client, session, arq_pool, admin_token):
    # Setup
    article = Article(title="Draft", content={"type":"doc"}, slug="draft", status="draft")
    session.add(article)
    session.commit()
    
    # Publish via API
    response = client.put(
        f"/api/articles/{article.id}",
        json={"status": "published", "send_newsletter": True},
        headers=admin_token
    )
    
    assert response.status_code == 200
    # Verify blast_newsletter_task was enqueued
    arq_pool.enqueue_job.assert_called_with("blast_newsletter_task", str(article.id), _defer_until=None)
