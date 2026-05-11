import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.subscriber import Subscriber
from app.models.article import Article
from app.models.newsletter_send import NewsletterSend
from app.config import settings
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
            "tags": [{"name": "newsletter_send_id", "value": send_id}],
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


class TestWebhookSignatureVerification:
    def test_invalid_signature_rejected(self, client: TestClient, monkeypatch):
        """Webhook with invalid Svix signature is rejected when secret is configured."""
        monkeypatch.setattr(settings, "RESEND_WEBHOOK_SECRET", "whsec_test_secret_12345678901234567890123")

        resp = client.post(
            "/api/webhooks/resend",
            json={"type": "email.opened", "data": {"tags": []}},
            headers={
                "svix-id": "msg_test123",
                "svix-timestamp": "1700000000",
                "svix-signature": "v1,invalid_signature_here",
            },
        )
        assert resp.status_code == 401

    def test_missing_signature_rejected(self, client: TestClient, monkeypatch):
        """Webhook without Svix headers is rejected when secret is configured."""
        monkeypatch.setattr(settings, "RESEND_WEBHOOK_SECRET", "whsec_test_secret_12345678901234567890123")

        resp = client.post(
            "/api/webhooks/resend",
            json={"type": "email.opened", "data": {"tags": []}},
        )
        assert resp.status_code == 401

    def test_no_secret_allows_processing(self, client: TestClient, monkeypatch):
        """Webhook is processed without signature verification when secret is not configured."""
        monkeypatch.setattr(settings, "RESEND_WEBHOOK_SECRET", "")

        resp = client.post(
            "/api/webhooks/resend",
            json={"type": "email.opened", "data": {"tags": [{"name": "newsletter_send_id", "value": str(uuid.uuid4())}]}},
        )
        # Should not be 401 - either 200 or some other processing result
        assert resp.status_code != 401


class TestBounceHandling:
    def _make_bounce_event(self, send_id: str, bounce_type: str, email: str = None, svix_id: str = None) -> dict:
        event = {
            "type": "email.bounced",
            "created_at": "2026-05-11T00:00:00.000Z",
            "data": {
                "to": [email or "test@example.com"],
                "tags": [{"name": "newsletter_send_id", "value": send_id}],
                "bounce": {
                    "type": bounce_type,
                    "subType": "Suppressed",
                    "message": "The recipient's email address is invalid.",
                },
            },
        }
        if svix_id:
            event["svix_id"] = svix_id
        return event

    def test_permanent_bounce_unsubscribes_subscriber(self, client: TestClient, session: Session):
        """Permanent bounce sets subscriber status to unsubscribed."""
        sub = _create_test_subscriber(session)
        send = _create_test_send(session, sub)

        event = self._make_bounce_event(str(send.id), "Permanent", email=sub.email, svix_id="msg_bounce_perm_1")

        resp = client.post("/api/webhooks/resend", json=event)
        assert resp.status_code == 200

        session.refresh(sub)
        assert sub.status == "unsubscribed"

        session.refresh(send)
        assert send.status == "failed"
        assert "Permanent" in send.error_message

    def test_transient_bounce_does_not_unsubscribe(self, client: TestClient, session: Session):
        """Transient bounce does NOT change subscriber status."""
        sub = _create_test_subscriber(session)
        send = _create_test_send(session, sub)

        event = self._make_bounce_event(str(send.id), "Transient", email=sub.email, svix_id="msg_bounce_transient_1")

        resp = client.post("/api/webhooks/resend", json=event)
        assert resp.status_code == 200

        session.refresh(sub)
        assert sub.status == "active"

        session.refresh(send)
        assert send.status == "failed"
        assert "Transient" in send.error_message


class TestComplaintHandling:
    def test_complaint_unsubscribes_subscriber(self, client: TestClient, session: Session):
        """Complaint events set subscriber status to unsubscribed."""
        sub = _create_test_subscriber(session)
        send = _create_test_send(session, sub)

        event = {
            "type": "email.complained",
            "created_at": "2026-05-11T00:00:00.000Z",
            "data": {
                "to": [sub.email],
                "tags": [{"name": "newsletter_send_id", "value": str(send.id)}],
            },
            "svix_id": "msg_complaint_1",
        }

        resp = client.post("/api/webhooks/resend", json=event)
        assert resp.status_code == 200

        session.refresh(sub)
        assert sub.status == "unsubscribed"

        session.refresh(send)
        assert send.status == "failed"
        assert send.error_message == "Complained"


class TestOpenClickTracking:
    def test_open_event_increments_open_count(self, client: TestClient, session: Session):
        """email.opened webhook increments open_count and sets opened_at."""
        sub = _create_test_subscriber(session)
        send = _create_test_send(session, sub)

        event = _make_open_event(str(send.id), svix_id="msg_open_1")

        resp = client.post("/api/webhooks/resend", json=event)
        assert resp.status_code == 200

        session.refresh(send)
        assert send.open_count == 1
        assert send.opened_at is not None

    def test_click_event_increments_click_count(self, client: TestClient, session: Session):
        """email.clicked webhook increments click_count and sets clicked_at."""
        sub = _create_test_subscriber(session)
        send = _create_test_send(session, sub)

        event = {
            "type": "email.clicked",
            "created_at": "2026-05-11T00:00:00.000Z",
            "data": {
                "tags": [{"name": "newsletter_send_id", "value": str(send.id)}],
            },
            "svix_id": "msg_click_1",
        }

        resp = client.post("/api/webhooks/resend", json=event)
        assert resp.status_code == 200

        session.refresh(send)
        assert send.click_count == 1
        assert send.clicked_at is not None

    def test_multiple_opens_and_clicks(self, client: TestClient, session: Session):
        """Multiple open and click events accumulate correctly."""
        sub = _create_test_subscriber(session)
        send = _create_test_send(session, sub)

        for i in range(3):
            open_event = _make_open_event(str(send.id), svix_id=f"msg_open_{i}")
            resp = client.post("/api/webhooks/resend", json=open_event)
            assert resp.status_code == 200

        for i in range(2):
            click_event = {
                "type": "email.clicked",
                "created_at": "2026-05-11T00:00:00.000Z",
                "data": {
                    "tags": [{"name": "newsletter_send_id", "value": str(send.id)}],
                },
                "svix_id": f"msg_click_{i}",
            }
            resp = client.post("/api/webhooks/resend", json=click_event)
            assert resp.status_code == 200

        session.refresh(send)
        assert send.open_count == 3
        assert send.click_count == 2
