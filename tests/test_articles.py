from fastapi.testclient import TestClient
from app.config import settings
from app.models.article import Article

AUTH_HEADER = {"Authorization": f"Bearer {settings.ADMIN_API_TOKEN}"}

def test_create_article(client: TestClient):
    response = client.post(
        "/api/admin/articles",
        json={"title": "Test Article", "content": {"type": "doc"}, "send_newsletter": True},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Article"
    assert data["slug"] == "test-article"
    assert data["status"] == "draft"

def test_create_article_slug_collision(client: TestClient):
    # Create first article
    client.post(
        "/api/admin/articles",
        json={"title": "Test Article", "content": {"type": "doc"}},
        headers=AUTH_HEADER,
    )
    # Create second with same title
    response = client.post(
        "/api/admin/articles",
        json={"title": "Test Article", "content": {"type": "doc"}},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "test-article-2"

def test_list_articles_only_published(client: TestClient, session):
    from app.services.article_service import create_article, update_article
    from datetime import datetime
    
    draft = create_article(session, "Draft Article", {"type": "doc"})
    published = create_article(session, "Published Article", {"type": "doc"})
    update_article(session, published, status="published", published_at=datetime.utcnow())
    
    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Published Article"

def test_get_article_by_slug(client: TestClient, session):
    from app.services.article_service import create_article, update_article
    from datetime import datetime
    
    article = create_article(session, "My Article", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.utcnow())
    
    response = client.get(f"/api/articles/{article.slug}")
    assert response.status_code == 200
    assert response.json()["title"] == "My Article"

def test_get_draft_article_returns_404(client: TestClient, session):
    from app.services.article_service import create_article
    
    article = create_article(session, "Draft", {"type": "doc"})
    response = client.get(f"/api/articles/{article.slug}")
    assert response.status_code == 404

def test_update_article(client: TestClient, session):
    from app.services.article_service import create_article
    
    article = create_article(session, "Original", {"type": "doc"})
    response = client.put(
        f"/api/articles/{article.id}",
        json={"title": "Updated"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

def test_publish_article(client: TestClient, session):
    from app.services.article_service import create_article
    
    article = create_article(session, "To Publish", {"type": "doc"})
    response = client.put(
        f"/api/articles/{article.id}",
        json={"status": "published"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["published_at"] is not None

def test_unpublish_article_fails(client: TestClient, session):
    from app.services.article_service import create_article, update_article
    from datetime import datetime
    
    article = create_article(session, "Published", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.utcnow())
    
    response = client.put(
        f"/api/articles/{article.id}",
        json={"status": "draft"},
        headers=AUTH_HEADER,
    )
    assert response.status_code == 400

def test_delete_article(client: TestClient, session):
    from app.services.article_service import create_article
    
    article = create_article(session, "To Delete", {"type": "doc"})
    response = client.delete(f"/api/articles/{article.id}", headers=AUTH_HEADER)
    assert response.status_code == 204

def test_article_crud_unauthorized(client: TestClient):
    response = client.post("/api/admin/articles", json={"title": "Test", "content": {}})
    assert response.status_code == 401

def test_admin_list_all_articles(client: TestClient, session):
    from app.services.article_service import create_article
    
    create_article(session, "Draft Article", {"type": "doc"})
    create_article(session, "Another Draft", {"type": "doc"})
    
    response = client.get("/api/admin/articles", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
