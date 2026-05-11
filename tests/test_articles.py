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
    from datetime import datetime
    
    draft = create_article(session, "Draft Article", {"type": "doc"})
    published = create_article(session, "Published Article", {"type": "doc"})
    update_article(session, published, status="published", published_at=datetime.utcnow())
    
    response = client.get("/api/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Published Article"

def test_get_article_by_slug(client: TestClient, session, admin_token):
    from app.services.article_service import create_article, update_article
    from datetime import datetime
    
    article = create_article(session, "My Article", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.utcnow())
    
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
    from datetime import datetime
    
    article = create_article(session, "Published", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.utcnow())
    
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
    from datetime import datetime
    
    article = create_article(session, "RSS Test Article", {"type": "doc", "content": [{"type": "text", "text": "Hello world"}]})
    update_article(session, article, status="published", published_at=datetime.utcnow(), description="A test article for RSS.")
    
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
    from datetime import datetime

    article = create_article(session, "Sitemap Article", {"type": "doc"})
    update_article(session, article, status="published", published_at=datetime.utcnow())

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
    from datetime import datetime

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
