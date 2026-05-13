import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.subscriber import Subscriber
from app.models.newsletter_send import NewsletterSend
import uuid


def _create_test_send(session: Session, status: str = "sent", error_message: str = None) -> NewsletterSend:
    send = NewsletterSend(
        subscriber_id=uuid.uuid4(),
        article_id=uuid.uuid4(),
        status=status,
        error_message=error_message,
    )
    session.add(send)
    session.commit()
    session.refresh(send)
    return send


class TestAnalyticsBounceComplaintMetrics:
    def test_analytics_includes_bounce_complaint_summary(self, client: TestClient, session: Session, admin_token):
        """Analytics endpoint returns bounce and complaint metrics in summary."""
        _create_test_send(session, status="sent")
        _create_test_send(session, status="failed", error_message="Bounced (Permanent): invalid")
        _create_test_send(session, status="failed", error_message="Complained")

        resp = client.get("/api/admin/analytics", headers=admin_token)
        assert resp.status_code == 200
        data = resp.json()

        assert "total_bounces" in data["summary"]
        assert "total_complaints" in data["summary"]
        assert "bounce_rate" in data["summary"]
        assert "complaint_rate" in data["summary"]
        assert data["summary"]["total_bounces"] == 1
        assert data["summary"]["total_complaints"] == 1

    def test_analytics_includes_bounce_complaint_growth(self, client: TestClient, session: Session, admin_token):
        """Analytics endpoint returns bounce and complaint time-series in growth."""
        _create_test_send(session, status="failed", error_message="Bounced (Permanent): invalid")
        _create_test_send(session, status="failed", error_message="Complained")

        resp = client.get("/api/admin/analytics", headers=admin_token)
        assert resp.status_code == 200
        data = resp.json()

        assert "bounces" in data["growth"]
        assert "complaints" in data["growth"]


class TestEndpointRoleTightening:
    """Analytics, performance, and newsletter endpoints should be admin-only."""

    def test_admin_can_access_analytics(self, client: TestClient, admin_token):
        resp = client.get("/api/admin/analytics", headers=admin_token)
        assert resp.status_code == 200

    def test_editor_cannot_access_analytics(self, client: TestClient, session: Session):
        from tests.conftest import create_user_token
        editor_token = create_user_token(session, "editor@test.com", role="editor")
        resp = client.get("/api/admin/analytics", headers=editor_token)
        assert resp.status_code == 403

    def test_contributor_cannot_access_analytics(self, client: TestClient, session: Session):
        from tests.conftest import create_user_token
        contrib_token = create_user_token(session, "contrib@test.com", role="contributor")
        resp = client.get("/api/admin/analytics", headers=contrib_token)
        assert resp.status_code == 403

    def test_admin_can_access_performance(self, client: TestClient, admin_token):
        resp = client.get("/api/admin/articles/performance", headers=admin_token)
        assert resp.status_code == 200

    def test_editor_cannot_access_performance(self, client: TestClient, session: Session):
        from tests.conftest import create_user_token
        editor_token = create_user_token(session, "editor2@test.com", role="editor")
        resp = client.get("/api/admin/articles/performance", headers=editor_token)
        assert resp.status_code == 403

    def test_contributor_cannot_access_performance(self, client: TestClient, session: Session):
        from tests.conftest import create_user_token
        contrib_token = create_user_token(session, "contrib2@test.com", role="contributor")
        resp = client.get("/api/admin/articles/performance", headers=contrib_token)
        assert resp.status_code == 403

    def test_editor_cannot_access_newsletter_status(self, client: TestClient, session: Session):
        from tests.conftest import create_user_token
        import uuid
        editor_token = create_user_token(session, "editor3@test.com", role="editor")
        resp = client.get(f"/api/admin/newsletter-blasts/{uuid.uuid4()}/status", headers=editor_token)
        assert resp.status_code == 403

    def test_contributor_cannot_access_newsletter_status(self, client: TestClient, session: Session):
        from tests.conftest import create_user_token
        import uuid
        contrib_token = create_user_token(session, "contrib3@test.com", role="contributor")
        resp = client.get(f"/api/admin/newsletter-blasts/{uuid.uuid4()}/status", headers=contrib_token)
        assert resp.status_code == 403
