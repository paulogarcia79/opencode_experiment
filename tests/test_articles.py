from fastapi.testclient import TestClient
from app.config import settings
from app.models.article import Article


def test_create_article(client: TestClient, admin_token):
    response = client.post(
        "/api/admin/articles",
        json={"title": "Test Article", "content": {"type": "doc"}, "send_newsletter": True},
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Article"
    assert data["slug"] == "test-article"
    assert data["status"] == "draft"

def test_create_article_slug_collision(client: TestClient, admin_token):
    # Create first article
    client.post(
        "/api/admin/articles",
        json={"title": "Test Article", "content": {"type": "doc"}},
        headers=admin_token,
    )
    # Create second with same title
    response = client.post(
        "/api/admin/articles",
        json={"title": "Test Article", "content": {"type": "doc"}},
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "test-article-2"

def test_list_articles_only_published(client: TestClient, session, admin_token):
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone
    
    draft = create_article(session, "Draft Article", {"type": "doc"})
    published = create_article(session, "Published Article", {"type": "doc"})
    update_article(session, published, status="published", published_at=datetime.now(timezone.utc))
    
    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Published Article"

def test_get_article_by_slug(client: TestClient, session, admin_token):
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone
    
    article = create_article(session, "My Article", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.now(timezone.utc))
    
    response = client.get(f"/api/articles/{article.slug}")
    assert response.status_code == 200
    assert response.json()["title"] == "My Article"

def test_get_draft_article_returns_404(client: TestClient, session, admin_token):
    from app.services.article_service import create_article
    
    article = create_article(session, "Draft", {"type": "doc"})
    response = client.get(f"/api/articles/{article.slug}")
    assert response.status_code == 404

def test_update_article(client: TestClient, session, admin_token):
    from app.services.article_service import create_article
    
    article = create_article(session, "Original", {"type": "doc"})
    response = client.put(
        f"/api/articles/{article.id}",
        json={"title": "Updated"},
        headers=admin_token,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

def test_publish_article(client: TestClient, session, admin_token):
    from app.services.article_service import create_article
    
    article = create_article(session, "To Publish", {"type": "doc"})
    response = client.put(
        f"/api/articles/{article.id}",
        json={"status": "published"},
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["published_at"] is not None

def test_unpublish_article_fails(client: TestClient, session, admin_token):
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone
    
    article = create_article(session, "Published", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.now(timezone.utc))
    
    response = client.put(
        f"/api/articles/{article.id}",
        json={"status": "draft"},
        headers=admin_token,
    )
    assert response.status_code == 400

def test_delete_article(client: TestClient, session, admin_token):
    from app.services.article_service import create_article
    
    article = create_article(session, "To Delete", {"type": "doc"})
    response = client.delete(f"/api/articles/{article.id}", headers=admin_token)
    assert response.status_code == 204

def test_delete_article_with_newsletter_sends(client: TestClient, session, admin_token):
    """Deleting an article with associated newsletter sends should not raise FK violation."""
    from app.services.article_service import create_article, update_article
    from app.models.newsletter_send import NewsletterSend
    from app.models.article_view import ArticleView
    from datetime import datetime, timezone
    import uuid
    
    article = create_article(session, "With Sends", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.now(timezone.utc))
    
    # Create related records
    send = NewsletterSend(
        article_id=article.id,
        subscriber_id=uuid.uuid4(),
        status="sent",
        open_count=1,
        click_count=0,
    )
    session.add(send)
    view = ArticleView(
        article_id=article.id,
        ip_hash="test_hash",
    )
    session.add(view)
    session.commit()
    
    response = client.delete(f"/api/articles/{article.id}", headers=admin_token)
    assert response.status_code == 204

def test_article_crud_unauthorized(client: TestClient, admin_token):
    response = client.post("/api/admin/articles", json={"title": "Test", "content": {}})
    assert response.status_code == 401

def test_admin_list_all_articles(client: TestClient, session, admin_token):
    from app.services.article_service import create_article
    
    create_article(session, "Draft Article", {"type": "doc"})
    create_article(session, "Another Draft", {"type": "doc"})
    
    response = client.get("/api/admin/articles", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_rss_feed(client: TestClient, session, admin_token):
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone
    
    article = create_article(session, "RSS Test Article", {"type": "doc", "content": [{"type": "text", "text": "Hello world"}]})
    update_article(session, article, status="published", published_at=datetime.now(timezone.utc), description="A test article for RSS.")
    
    response = client.get("/feed.xml")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/atom+xml"
    content = response.text
    assert "<feed xmlns=\"http://www.w3.org/2005/Atom\">" in content
    assert "RSS Test Article" in content
    assert "/articles/rss-test-article" in content
    assert "A test article for RSS." in content

def test_rss_feed_excludes_drafts(client: TestClient, session, admin_token):
    from app.services.article_service import create_article
    
    create_article(session, "Draft Only", {"type": "doc"})
    
    response = client.get("/feed.xml")
    assert response.status_code == 200
    content = response.text
    assert "Draft Only" not in content


def test_sitemap_xml(client: TestClient, session, admin_token):
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone

    article = create_article(session, "Sitemap Article", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    content = response.text
    assert "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">" in content
    assert "<loc>http://localhost/</loc>" in content
    assert f"<loc>http://localhost/articles/{article.slug}</loc>" in content
    assert "<loc>http://localhost/feed.xml</loc>" in content
    assert "<lastmod>" in content


def test_sitemap_excludes_drafts(client: TestClient, session, admin_token):
    from app.services.article_service import create_article

    create_article(session, "Draft Sitemap", {"type": "doc"})

    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    content = response.text
    assert "Draft Sitemap" not in content


def test_sitemap_lastmod_for_homepage_uses_latest_published_at(client: TestClient, session, admin_token):
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone

    article = create_article(session, "Homepage Lastmod", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime(2025, 1, 15, 10, 0, 0))

    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    content = response.text
    assert "2025-01-15T10:00:00" in content


def test_robots_txt(client: TestClient, admin_token):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    content = response.text
    assert "User-agent: *" in content
    assert "Disallow: /admin/" in content
    assert "Disallow: /api/" in content
    assert "Disallow: /uploads/" in content
    assert "Sitemap:" in content
    assert "/sitemap.xml" in content

def test_preview_email_endpoint(client: TestClient, session, admin_token):
    from app.services.article_service import create_article
    from unittest.mock import patch
    from app.models.user import User
    from sqlmodel import select
    
    article = create_article(session, "Preview Test", {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Preview content"}]}]})
    
    with patch('app.services.email_service.send_newsletter_email') as mock_send:
        response = client.post(f"/api/admin/articles/{article.id}/preview-email", headers=admin_token)
        
    assert response.status_code == 200
    assert response.json()["message"] == "Preview sent successfully"
    
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == settings.ADMIN_EMAIL
    assert args[1] == "Preview Test"
    assert "Preview content" in args[2]
    assert args[3] == "preview-mode-no-unsubscribe"

def test_create_article_sets_author_id(client: TestClient, session, admin_token):
    """Article creation should set author_id from authenticated user."""
    from app.models.user import User
    from sqlmodel import select
    import uuid
    
    admin = session.exec(select(User)).first()
    
    response = client.post(
        "/api/admin/articles",
        json={"title": "Authored Article", "content": {"type": "doc"}, "send_newsletter": True},
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["author_id"] == str(admin.id)
    
    # Verify in database
    from app.models.article import Article
    article = session.get(Article, uuid.UUID(data["id"]))
    assert article.author_id == admin.id

def test_create_article_response_includes_author(client: TestClient, session, admin_token):
    """Article creation response should include author email."""
    from app.models.user import User
    from sqlmodel import select
    
    admin = session.exec(select(User)).first()
    
    response = client.post(
        "/api/admin/articles",
        json={"title": "Author Display Test", "content": {"type": "doc"}, "send_newsletter": True},
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert "author" in data
    assert data["author"]["email"] == admin.email

def test_list_admin_articles_includes_author(client: TestClient, session, admin_token):
    """Admin articles list should include author information."""
    from app.models.user import User
    from sqlmodel import select
    
    admin = session.exec(select(User)).first()
    
    client.post(
        "/api/admin/articles",
        json={"title": "List Test Article", "content": {"type": "doc"}},
        headers=admin_token,
    )
    
    response = client.get("/api/admin/articles", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"]["email"] == admin.email

def test_autosave_sets_author_id(client: TestClient, session, admin_token):
    """Autosave article creation should set author_id from authenticated user."""
    from app.models.user import User
    from sqlmodel import select
    
    admin = session.exec(select(User)).first()
    
    response = client.post(
        "/api/admin/articles/autosave",
        json={"title": "Autosaved Article", "content": {"type": "doc"}},
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["author_id"] == str(admin.id)


def test_article_accepts_pending_review_status(session):
    """Article model should accept 'pending_review' as a valid status."""
    from app.models.article import Article
    import uuid

    article = Article(
        title="Review Me",
        slug=f"review-me-{uuid.uuid4().hex[:8]}",
        content={"type": "doc"},
        status="pending_review",
    )
    session.add(article)
    session.commit()
    session.refresh(article)

    assert article.status == "pending_review"


def test_article_has_submitted_at_field(session):
    """Article model should have a submitted_at datetime field that persists."""
    from datetime import datetime, timezone
    from app.models.article import Article
    import uuid

    article = Article(
        title="Submit Test",
        slug=f"submit-test-{uuid.uuid4().hex[:8]}",
        content={"type": "doc"},
        status="pending_review",
        submitted_at=datetime(2026, 5, 12, 10, 0, 0, tzinfo=timezone.utc),
    )
    session.add(article)
    session.commit()
    session.refresh(article)

    assert article.submitted_at is not None
    assert article.submitted_at.year == 2026
    assert article.submitted_at.month == 5


def test_review_action_model_creation(session):
    """ReviewAction model should persist with FK relationships to Article and User."""
    from datetime import datetime, timezone
    from app.models.review_action import ReviewAction
    from app.models.article import Article
    from app.models.user import User
    from sqlmodel import select
    import uuid

    article = Article(
        title="Review Test",
        slug=f"review-test-{uuid.uuid4().hex[:8]}",
        content={"type": "doc"},
        status="pending_review",
    )
    session.add(article)
    session.commit()
    session.refresh(article)

    reviewer = session.exec(select(User)).first()

    review_action = ReviewAction(
        article_id=article.id,
        reviewer_id=reviewer.id,
        action="rejected",
        feedback="Needs more detail in section 2",
    )
    session.add(review_action)
    session.commit()
    session.refresh(review_action)

    assert review_action.id is not None
    assert review_action.article_id == article.id
    assert review_action.reviewer_id == reviewer.id
    assert review_action.action == "rejected"
    assert review_action.feedback == "Needs more detail in section 2"
    assert review_action.created_at is not None


def test_pending_review_article_not_in_public_list(client: TestClient, session, admin_token):
    """Public article list should not include pending_review articles."""
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone

    draft = create_article(session, "Draft", {"type": "doc"})
    published = create_article(session, "Published", {"type": "doc"})
    pending = create_article(session, "Pending Review", {"type": "doc"})
    update_article(session, published, status="published", published_at=datetime.now(timezone.utc))
    pending.status = "pending_review"
    session.add(pending)
    session.commit()

    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    titles = [a["title"] for a in data]
    assert "Published" in titles
    assert "Draft" not in titles
    assert "Pending Review" not in titles


def test_pending_review_article_returns_404(client: TestClient, session, admin_token):
    """Public article detail should return 404 for pending_review articles."""
    from app.services.article_service import create_article

    article = create_article(session, "Pending Review Slug Test", {"type": "doc"})
    article.status = "pending_review"
    session.add(article)
    session.commit()

    response = client.get(f"/api/articles/{article.slug}")
    assert response.status_code == 404


def test_admin_articles_sort_by_title(client: TestClient, session, admin_token):
    """Admin article list should sort by title via query param."""
    from app.services.article_service import create_article

    create_article(session, "Zebra Article", {"type": "doc"})
    create_article(session, "Alpha Article", {"type": "doc"})
    create_article(session, "Middle Article", {"type": "doc"})

    response = client.get("/api/admin/articles?sort=title&order=asc", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    titles = [a["title"] for a in data]
    assert titles == ["Alpha Article", "Middle Article", "Zebra Article"]

    response = client.get("/api/admin/articles?sort=title&order=desc", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    titles = [a["title"] for a in data]
    assert titles == ["Zebra Article", "Middle Article", "Alpha Article"]


def test_admin_articles_filter_by_status(client: TestClient, session, admin_token):
    """Admin article list should filter by status via query param."""
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone

    create_article(session, "Draft One", {"type": "doc"})
    create_article(session, "Draft Two", {"type": "doc"})
    pub = create_article(session, "Published One", {"type": "doc"})
    update_article(session, pub, status="published", published_at=datetime.now(timezone.utc))

    response = client.get("/api/admin/articles?status=published", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Published One"

    response = client.get("/api/admin/articles?status=draft", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(a["status"] == "draft" for a in data)


def test_contributor_sees_only_own_articles(client: TestClient, session):
    """Contributor listing admin articles should only see their own."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article

    contrib = create_user(session, "contrib01@test.com", role="contributor")
    other = create_user(session, "other01@test.com", role="contributor")
    contrib_token = get_token_for_user(contrib)

    create_article(session, "My Article", {"type": "doc"}, author_id=contrib.id)
    create_article(session, "Not Mine", {"type": "doc"}, author_id=other.id)

    response = client.get("/api/admin/articles", headers=contrib_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "My Article"


def test_contributor_gets_404_on_non_owned_article(client: TestClient, session):
    """Contributor requesting another's article by ID should get 404."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article

    contrib = create_user(session, "contrib02@test.com", role="contributor")
    other = create_user(session, "other02@test.com", role="contributor")
    contrib_token = get_token_for_user(contrib)

    article = create_article(session, "Other Article", {"type": "doc"}, author_id=other.id)

    response = client.get(f"/api/admin/articles/{article.id}", headers=contrib_token)
    assert response.status_code == 404


def test_admin_articles_invalid_sort_column_returns_400(client: TestClient, admin_token):
    """Invalid sort column should return 400 Bad Request."""
    response = client.get("/api/admin/articles?sort=malicious;DROP TABLE", headers=admin_token)
    assert response.status_code == 400


def test_admin_articles_invalid_order_returns_400(client: TestClient, admin_token):
    """Invalid order should return 400 Bad Request."""
    response = client.get("/api/admin/articles?sort=title&order=random", headers=admin_token)
    assert response.status_code == 400


def test_contributor_submits_article_for_review(client: TestClient, session):
    """Contributor submitting own article sets status to pending_review and sets submitted_at."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article

    contrib = create_user(session, "submitter@test.com", role="contributor")
    token = get_token_for_user(contrib)
    article = create_article(session, "My Draft", {"type": "doc"}, author_id=contrib.id)

    response = client.post(f"/api/admin/articles/{article.id}/submit-review", headers=token)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_review"
    assert data["submitted_at"] is not None


def test_editor_approves_article(client: TestClient, session):
    """Editor approving a pending_review article publishes it and creates a ReviewAction."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article
    from app.models.review_action import ReviewAction
    from sqlmodel import select
    from datetime import datetime, timezone

    contrib = create_user(session, "contrib-approve@test.com", role="contributor")
    editor = create_user(session, "editor-approve@test.com", role="editor")
    editor_token = get_token_for_user(editor)
    article = create_article(session, "Approve Me", {"type": "doc"}, author_id=contrib.id)
    article.status = "pending_review"
    article.submitted_at = datetime.now(timezone.utc)
    session.add(article)
    session.commit()

    response = client.post(f"/api/admin/articles/{article.id}/approve", headers=editor_token)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["published_at"] is not None
    assert data["submitted_at"] is None

    review_actions = session.exec(
        select(ReviewAction).where(ReviewAction.article_id == article.id)
    ).all()
    assert len(review_actions) == 1
    assert review_actions[0].action == "approved"
    assert review_actions[0].reviewer_id == editor.id


def test_editor_rejects_article_with_feedback(client: TestClient, session):
    """Editor rejecting a pending_review article sets it to draft and stores feedback."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article
    from app.models.review_action import ReviewAction
    from sqlmodel import select
    from datetime import datetime, timezone

    contrib = create_user(session, "contrib-reject@test.com", role="contributor")
    editor = create_user(session, "editor-reject@test.com", role="editor")
    editor_token = get_token_for_user(editor)
    article = create_article(session, "Reject Me", {"type": "doc"}, author_id=contrib.id)
    article.status = "pending_review"
    article.submitted_at = datetime.now(timezone.utc)
    session.add(article)
    session.commit()

    response = client.post(
        f"/api/admin/articles/{article.id}/reject",
        json={"feedback": "Needs more research in section 3"},
        headers=editor_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "draft"
    assert data["submitted_at"] is None

    review_actions = session.exec(
        select(ReviewAction).where(ReviewAction.article_id == article.id)
    ).all()
    assert len(review_actions) == 1
    assert review_actions[0].action == "rejected"
    assert review_actions[0].feedback == "Needs more research in section 3"
    assert review_actions[0].reviewer_id == editor.id


def test_review_queue_returns_pending_review_articles(client: TestClient, session):
    """Review queue endpoint returns all pending_review articles with author info."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article
    from datetime import datetime, timezone

    editor = create_user(session, "editor-queue@test.com", role="editor")
    editor_token = get_token_for_user(editor)
    contrib = create_user(session, "contrib-queue@test.com", role="contributor")

    a1 = create_article(session, "Pending 1", {"type": "doc"}, author_id=contrib.id)
    a1.status = "pending_review"
    a1.submitted_at = datetime.now(timezone.utc)
    a2 = create_article(session, "Pending 2", {"type": "doc"}, author_id=contrib.id)
    a2.status = "pending_review"
    a2.submitted_at = datetime.now(timezone.utc)
    create_article(session, "Draft", {"type": "doc"}, author_id=contrib.id)
    session.commit()

    response = client.get("/api/admin/articles/review", headers=editor_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["status"] == "pending_review"
    assert data[0]["submitted_at"] is not None
    assert data[0]["author"] is not None


def test_review_count_returns_pending_count(client: TestClient, session):
    """Review count endpoint returns the number of pending_review articles."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article
    from datetime import datetime, timezone

    editor = create_user(session, "editor-count@test.com", role="editor")
    editor_token = get_token_for_user(editor)
    contrib = create_user(session, "contrib-count@test.com", role="contributor")

    a1 = create_article(session, "P 1", {"type": "doc"}, author_id=contrib.id)
    a1.status = "pending_review"
    a1.submitted_at = datetime.now(timezone.utc)
    a2 = create_article(session, "P 2", {"type": "doc"}, author_id=contrib.id)
    a2.status = "pending_review"
    a2.submitted_at = datetime.now(timezone.utc)
    session.commit()

    response = client.get("/api/admin/articles/review/count", headers=editor_token)
    assert response.status_code == 200
    data = response.json()
    assert data["pending_count"] == 2


def test_contributor_cannot_approve(client: TestClient, session):
    """Contributor should get 403 when trying to approve."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article

    contrib = create_user(session, "contrib-noapprove@test.com", role="contributor")
    token = get_token_for_user(contrib)
    article = create_article(session, "No Approve", {"type": "doc"}, author_id=contrib.id)
    article.status = "pending_review"
    session.commit()

    response = client.post(f"/api/admin/articles/{article.id}/approve", headers=token)
    assert response.status_code == 403


def test_contributor_cannot_reject(client: TestClient, session):
    """Contributor should get 403 when trying to reject."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article

    contrib = create_user(session, "contrib-noreject@test.com", role="contributor")
    token = get_token_for_user(contrib)
    article = create_article(session, "No Reject", {"type": "doc"}, author_id=contrib.id)
    article.status = "pending_review"
    session.commit()

    response = client.post(f"/api/admin/articles/{article.id}/reject", json={"feedback": "nope"}, headers=token)
    assert response.status_code == 403


def test_contributor_cannot_submit_non_owned(client: TestClient, session):
    """Contributor should get 403 when submitting another user's article."""
    from tests.conftest import create_user, get_token_for_user
    from app.services.article_service import create_article

    contrib = create_user(session, "contrib-other@test.com", role="contributor")
    other = create_user(session, "other-owner@test.com", role="contributor")
    token = get_token_for_user(contrib)
    article = create_article(session, "Not Yours", {"type": "doc"}, author_id=other.id)

    response = client.post(f"/api/admin/articles/{article.id}/submit-review", headers=token)
    assert response.status_code == 403


def test_admin_article_detail_includes_author(client: TestClient, session, admin_token):
    """Admin article detail endpoint should return author info in the response."""
    from app.services.article_service import create_article
    from app.models.user import User
    from sqlmodel import select

    admin = session.exec(select(User)).first()
    article = create_article(session, "Author Test", {"type": "doc"}, author_id=admin.id)

    response = client.get(f"/api/admin/articles/{article.id}", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert data["author"] is not None
    assert data["author"]["id"] == str(admin.id)
    assert data["author"]["email"] == admin.email
