import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.subscriber import Subscriber
from app.models.article import Article
from app.models.newsletter_send import NewsletterSend
import uuid


def _create_test_subscriber(session: Session) -> Subscriber:
    sub = Subscriber(
        email=f"test-{uuid.uuid4()}@example.com",
        status="active",
        confirmation_token=uuid.uuid4().hex,
    )
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def _create_test_send(session: Session, subscriber: Subscriber) -> NewsletterSend:
    send = NewsletterSend(
        subscriber_id=subscriber.id,
        article_id=uuid.uuid4(),
        status="sent",
    )
    session.add(send)
    session.commit()
    session.refresh(send)
    return send


def _make_open_event(send_id: str, svix_id: str = None) -> dict:
    event = {
        "type": "email.opened",
        "created_at": "2026-05-11T00:00:00.000Z",
        "data": {
            "tags": {"newsletter_send_id": send_id},
        },
    }
    if svix_id:
        event["svix_id"] = svix_id
    return event


class TestWebhookIdempotency:
    def test_duplicate_event_is_skipped(self, client: TestClient, session: Session):
        """Sending the same webhook event twice (same svix_id) only processes once."""
        sub = _create_test_subscriber(session)
        send = _create_test_send(session, sub)
        svix_id = "msg_test_duplicate_123"

        event = _make_open_event(str(send.id), svix_id)

        # First delivery
        resp1 = client.post("/api/webhooks/resend", json=event)
        assert resp1.status_code == 200

        session.refresh(send)
        first_open_count = send.open_count

        # Second delivery (duplicate)
        resp2 = client.post("/api/webhooks/resend", json=event)
        assert resp2.status_code == 200

        session.refresh(send)
        # open_count should NOT have increased
        assert send.open_count == first_open_count

    def test_new_event_is_processed(self, client: TestClient, session: Session):
        """A new webhook event with a unique svix_id is processed normally."""
        sub = _create_test_subscriber(session)
        send = _create_test_send(session, sub)

        event1 = _make_open_event(str(send.id), "msg_test_unique_1")
        event2 = _make_open_event(str(send.id), "msg_test_unique_2")

        resp1 = client.post("/api/webhooks/resend", json=event1)
        assert resp1.status_code == 200

        resp2 = client.post("/api/webhooks/resend", json=event2)
        assert resp2.status_code == 200

        session.refresh(send)
        # Both unique events should be processed
        assert send.open_count == 2
