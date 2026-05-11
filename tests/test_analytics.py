import pytest
import uuid
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from app.models.subscriber import Subscriber
from app.models.newsletter_send import NewsletterSend

def test_get_analytics_unauthorized(client: TestClient):
    response = client.get("/api/admin/analytics")
    assert response.status_code == 401

def test_get_analytics_success(client: TestClient, session, admin_token):
    # Setup some data
    now = datetime.now(timezone.utc)
    
    # Active subscriber from today
    sub1 = Subscriber(email="today@ex.com", status="active", created_at=now, confirmation_token="t1")
    # Unsubscribed yesterday
    sub2 = Subscriber(email="yesterday@ex.com", status="unsubscribed", created_at=now - timedelta(days=1), updated_at=now - timedelta(days=1), confirmation_token="t2")
    
    session.add_all([sub1, sub2])
    
    # Newsletter sends
    s1 = NewsletterSend(article_id=uuid.uuid4(), subscriber_id=sub1.id, status="sent", created_at=now)
    s2 = NewsletterSend(article_id=uuid.uuid4(), subscriber_id=sub1.id, status="failed", error_message="Bounced", created_at=now)
    session.add_all([s1, s2])
    
    session.commit()

    response = client.get("/api/admin/analytics?range=7d", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    
    assert "growth" in data
    assert "delivery" in data
    assert "summary" in data
    assert data["summary"]["total_active"] == 1
    assert data["summary"]["total_unsubscribed"] == 1
    
    # Verify delivery stats
    assert data["delivery"]["sent"] == 1
    assert data["delivery"]["failed"] == 1
    
    # Verify growth chart data
    assert len(data["growth"]["signups"]) > 0
    assert len(data["growth"]["unsubscribes"]) > 0
    
    # Check today's signup
    today_signup = [s for s in data["growth"]["signups"] if s["date"] == now.strftime('%Y-%m-%d')]
    assert len(today_signup) == 1
    assert today_signup[0]["count"] == 1
