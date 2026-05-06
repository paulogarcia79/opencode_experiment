from fastapi.testclient import TestClient
from sqlmodel import select
from app.models.subscriber import Subscriber

def test_subscribe_creates_pending_subscriber(client: TestClient, session):
    response = client.post("/api/subscribers", json={"email": "test@example.com"})
    assert response.status_code == 200
    assert "Check your email" in response.json()["message"]
    
    subscriber = session.get(Subscriber, response.json().get("id")) or session.exec(select(Subscriber).where(Subscriber.email == "test@example.com")).first()
    assert subscriber is not None
    assert subscriber.status == "pending"
    assert len(subscriber.confirmation_token) > 0

def test_subscribe_duplicate_returns_existing(client: TestClient, session):
    from app.services.subscriber_service import create_subscriber
    
    sub1 = create_subscriber(session, "dup@example.com")
    response = client.post("/api/subscribers", json={"email": "dup@example.com"})
    assert response.status_code == 200
    
    subs = session.exec(select(Subscriber).where(Subscriber.email == "dup@example.com")).all()
    assert len(subs) == 1

def test_confirm_subscriber(client: TestClient, session):
    from app.services.subscriber_service import create_subscriber
    
    subscriber = create_subscriber(session, "confirm@example.com")
    response = client.get(f"/api/subscribers/confirm?token={subscriber.confirmation_token}")
    assert response.status_code == 200
    assert "confirmed" in response.json()["message"]
    
    session.refresh(subscriber)
    assert subscriber.status == "active"

def test_confirm_invalid_token(client: TestClient):
    response = client.get("/api/subscribers/confirm?token=invalid-token")
    assert response.status_code == 400

def test_unsubscribe(client: TestClient, session):
    from app.services.subscriber_service import create_subscriber, confirm_subscriber
    
    subscriber = create_subscriber(session, "unsub@example.com")
    confirm_subscriber(session, subscriber.confirmation_token)
    
    response = client.get(f"/api/subscribers/unsubscribe?token={subscriber.confirmation_token}")
    assert response.status_code == 200
    assert "unsubscribed" in response.json()["message"]
    
    session.refresh(subscriber)
    assert subscriber.status == "unsubscribed"

def test_unsubscribe_invalid_token(client: TestClient):
    response = client.get("/api/subscribers/unsubscribe?token=invalid")
    assert response.status_code == 400
