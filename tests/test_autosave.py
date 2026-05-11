from fastapi.testclient import TestClient
from app.config import settings
from app.models.article import Article



def test_autosave_existing_draft(client: TestClient, session, admin_token):
    """Auto-saving an existing draft updates its content without publishing."""
    from app.services.article_service import create_article

    article = create_article(session, "Draft Title", {"type": "doc"})

    response = client.put(
        f"/api/admin/articles/{article.id}/autosave",
        json={
            "title": "Updated Draft Title",
            "content": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]}]},
            "description": "Updated desc",
            "tag_names": ["python"],
        },
        headers=admin_token,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Draft Title"
    assert data["description"] == "Updated desc"
    assert data["status"] == "draft"
    assert data["slug"] == "draft-title"
    assert any(t["name"] == "python" for t in data["tags"])


def test_autosave_keeps_draft_status(client: TestClient, session, admin_token):
    """Auto-save must never publish an article, even if status is passed."""
    from app.services.article_service import create_article, update_article
    from datetime import datetime, timezone

    article = create_article(session, "Draft", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.now(timezone.utc))

    response = client.put(
        f"/api/admin/articles/{article.id}/autosave",
        json={"title": "Updated"},
        headers=admin_token,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "draft"
    assert data["published_at"] is None


def test_autosave_unauthorized(client: TestClient, session, admin_token):
    """Auto-save requires admin authentication."""
    from app.services.article_service import create_article

    article = create_article(session, "Draft", {"type": "doc"})

    response = client.put(
        f"/api/admin/articles/{article.id}/autosave",
        json={"title": "Updated"},
    )
    assert response.status_code == 401


def test_autosave_invalid_token(client: TestClient, session, admin_token):
    """Auto-save rejects invalid bearer tokens."""
    from app.services.article_service import create_article

    article = create_article(session, "Draft", {"type": "doc"})

    response = client.put(
        f"/api/admin/articles/{article.id}/autosave",
        json={"title": "Updated"},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401


def test_autosave_nonexistent_article(client: TestClient, admin_token):
    """Auto-saving a non-existent article returns 404."""
    import uuid

    response = client.put(
        f"/api/admin/articles/{uuid.uuid4()}/autosave",
        json={"title": "Updated"},
        headers=admin_token,
    )
    assert response.status_code == 404


def test_autosave_create_new_article(client: TestClient, admin_token):
    """Auto-save can create a brand-new draft article."""
    response = client.post(
        "/api/admin/articles/autosave",
        json={
            "title": "New Draft",
            "content": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]}]},
            "description": "A new draft",
            "tag_names": ["vue"],
        },
        headers=admin_token,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["slug"] == "new-draft"
    assert data["title"] == "New Draft"
    assert data["status"] == "draft"


def test_autosave_create_unauthorized(client: TestClient, admin_token):
    """Creating a new article via auto-save requires admin auth."""
    response = client.post(
        "/api/admin/articles/autosave",
        json={"title": "New Draft", "content": {"type": "doc"}},
    )
    assert response.status_code == 401
