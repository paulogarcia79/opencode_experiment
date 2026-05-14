import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select, func
from app.models.article import Article
from app.models.article_view import ArticleView
from app.services.article_service import create_article, update_article
from datetime import datetime, timedelta, timezone
import uuid
import hashlib


class TestArticleViewTracking:
    def test_post_view_endpoint_records_view(self, client: TestClient, session: Session, admin_token):
        article = create_article(session, "Viewed Article", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        response = client.post(f"/api/articles/{article.slug}/view")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        views = session.exec(
            select(ArticleView).where(ArticleView.article_id == article.id)
        ).all()
        assert len(views) == 1
        assert views[0].article_id == article.id

    def test_get_published_article_no_longer_records_view(self, client: TestClient, session: Session, admin_token):
        article = create_article(session, "Not Viewed Article", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        response = client.get(f"/api/articles/{article.slug}")
        assert response.status_code == 200

        views = session.exec(
            select(ArticleView).where(ArticleView.article_id == article.id)
        ).all()
        assert len(views) == 0

    def test_duplicate_view_within_24h_not_recorded(self, client: TestClient, session: Session, admin_token):
        article = create_article(session, "Dup Test", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        # First view
        response = client.post(f"/api/articles/{article.slug}/view")
        assert response.status_code == 200

        # Second view (same IP, within 24h)
        response = client.post(f"/api/articles/{article.slug}/view")
        assert response.status_code == 200

        count = session.exec(
            select(func.count(ArticleView.id)).where(ArticleView.article_id == article.id)
        ).first()
        assert count == 1

    def test_view_after_24h_recorded(self, client: TestClient, session: Session, admin_token):
        article = create_article(session, "Old View", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        # Insert a view from 25 hours ago
        old_view = ArticleView(
            article_id=article.id,
            ip_hash=hashlib.sha256("127.0.0.1".encode()).hexdigest(),
            viewed_at=datetime.now(timezone.utc) - timedelta(hours=25),
        )
        session.add(old_view)
        session.commit()

        # New view should be recorded
        response = client.post(f"/api/articles/{article.slug}/view")
        assert response.status_code == 200

        count = session.exec(
            select(func.count(ArticleView.id)).where(ArticleView.article_id == article.id)
        ).first()
        assert count == 2

    def test_different_ips_both_recorded(self, client: TestClient, session: Session, admin_token):
        """Different IPs should both be recorded even within 24h."""
        article = create_article(session, "Multi IP", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        # First view from IP 1
        response = client.post(f"/api/articles/{article.slug}/view")
        assert response.status_code == 200

        # Manually insert a view from a different IP
        other_view = ArticleView(
            article_id=article.id,
            ip_hash=hashlib.sha256("10.0.0.1".encode()).hexdigest(),
            viewed_at=datetime.now(timezone.utc),
        )
        session.add(other_view)
        session.commit()

        count = session.exec(
            select(func.count(ArticleView.id)).where(ArticleView.article_id == article.id)
        ).first()
        assert count == 2

    def test_draft_article_no_view_recorded(self, client: TestClient, session: Session, admin_token):
        article = create_article(session, "Draft", {"type": "doc"})

        response = client.post(f"/api/articles/{article.slug}/view")
        assert response.status_code == 404

        count = session.exec(
            select(func.count(ArticleView.id)).where(ArticleView.article_id == article.id)
        ).first()
        assert count == 0


class TestArticlePerformanceAnalytics:
    def test_article_analytics_endpoint_returns_views(self, client: TestClient, session: Session, admin_token):
        article = create_article(session, "Analytics Test", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        # Record some views
        for i in range(5):
            view = ArticleView(
                article_id=article.id,
                ip_hash=hashlib.sha256(f"192.168.1.{i}".encode()).hexdigest(),
                viewed_at=datetime.now(timezone.utc),
            )
            session.add(view)
        session.commit()

        response = client.get(f"/api/admin/articles/{article.id}/analytics", headers=admin_token)
        assert response.status_code == 200
        data = response.json()

        assert "total_views" in data
        assert "unique_views_24h" in data
        assert data["total_views"] == 5
        assert data["unique_views_24h"] == 5

    def test_article_analytics_includes_email_metrics(self, client: TestClient, session: Session, admin_token):
        from app.models.newsletter_send import NewsletterSend

        article = create_article(session, "Email Analytics", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        # Create newsletter sends with engagement
        for i in range(10):
            send = NewsletterSend(
                article_id=article.id,
                subscriber_id=uuid.uuid4(),
                status="sent",
                open_count=i % 3,
                click_count=1 if i % 2 == 0 else 0,
            )
            session.add(send)
        session.commit()

        response = client.get(f"/api/admin/articles/{article.id}/analytics", headers=admin_token)
        assert response.status_code == 200
        data = response.json()

        assert "email_sent" in data
        assert "email_opens" in data
        assert "email_clicks" in data
        assert "email_open_rate" in data
        assert "email_ctr" in data
        assert data["email_sent"] == 10

    def test_article_analytics_unauthorized(self, client: TestClient, session: Session):
        article = create_article(session, "Unauthorized", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        response = client.get(f"/api/admin/articles/{article.id}/analytics")
        assert response.status_code == 401

    def test_article_analytics_not_found(self, client: TestClient, admin_token):
        fake_id = uuid.uuid4()
        response = client.get(f"/api/admin/articles/{fake_id}/analytics", headers=admin_token)
        assert response.status_code == 404


class TestArticlesPerformanceList:
    def test_performance_list_returns_articles_with_metrics(self, client: TestClient, session: Session, admin_token):
        from app.models.newsletter_send import NewsletterSend

        article1 = create_article(session, "Popular Article", {"type": "doc"})
        update_article(session, article1, status="published", published_at=datetime.now(timezone.utc))

        article2 = create_article(session, "Draft Article", {"type": "doc"})

        # Add views to article1
        for i in range(10):
            view = ArticleView(
                article_id=article1.id,
                ip_hash=hashlib.sha256(f"192.168.1.{i}".encode()).hexdigest(),
                viewed_at=datetime.now(timezone.utc),
            )
            session.add(view)

        # Add newsletter sends to article1
        for i in range(5):
            send = NewsletterSend(
                article_id=article1.id,
                subscriber_id=uuid.uuid4(),
                status="sent",
                open_count=2,
                click_count=1,
            )
            session.add(send)
        session.commit()

        response = client.get("/api/admin/articles/performance", headers=admin_token)
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        popular = next(a for a in data if a["id"] == str(article1.id))
        assert popular["total_views"] == 10
        assert popular["email_sent"] == 5
        assert popular["email_opens"] == 10
        assert popular["email_clicks"] == 5

        draft = next(a for a in data if a["id"] == str(article2.id))
        assert draft["total_views"] == 0
        assert draft["email_sent"] == 0

    def test_performance_list_unauthorized(self, client: TestClient, session: Session):
        article = create_article(session, "Unauthorized", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

        response = client.get("/api/admin/articles/performance")
        assert response.status_code == 401


class TestNonPublishedArticleAccess:
    def test_non_published_returns_404_for_public(self, client: TestClient, session: Session):
        article = create_article(session, "Secret Draft", {"type": "doc"})
        response = client.get(f"/api/articles/{article.slug}")
        assert response.status_code == 404

    def test_non_published_allowed_for_editor(self, client: TestClient, session: Session):
        from tests.conftest import create_user_token
        article = create_article(session, "Editor Sees Draft", {"type": "doc"})
        editor_headers = create_user_token(session, "editor-sees@test.com", "editor")
        response = client.get(f"/api/articles/{article.slug}", headers=editor_headers)
        assert response.status_code == 200

    def test_non_published_allowed_for_admin(self, client: TestClient, session: Session, admin_token):
        article = create_article(session, "Admin Sees Draft", {"type": "doc"})
        response = client.get(f"/api/articles/{article.slug}", headers=admin_token)
        assert response.status_code == 200
