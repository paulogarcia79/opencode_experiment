from fastapi.testclient import TestClient
from app.config import settings

AUTH_HEADER = {"Authorization": f"Bearer {settings.ADMIN_API_TOKEN}"}


class TestSearchEndpoint:
    def test_search_returns_200_with_matching_article(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        article = create_article(session, "Docker Compose Guide", {"type": "doc", "content": [{"type": "text", "text": "Learn docker compose networking"}]})
        update_article(session, article, status="published", published_at=datetime.utcnow())

        response = client.get("/api/articles/search?q=docker")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Docker Compose Guide"

    def test_search_finds_by_title(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        article = create_article(session, "Advanced Vue Patterns", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.utcnow())

        response = client.get("/api/articles/search?q=vue")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Advanced Vue Patterns"

    def test_search_finds_by_description(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        article = create_article(session, "Article", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.utcnow(), description="Game design principles for indie developers")

        response = client.get("/api/articles/search?q=indie")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["description"] == "Game design principles for indie developers"

    def test_search_finds_by_content(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        article = create_article(session, "Networking Guide", {"type": "doc", "content": [{"type": "text", "text": "Understanding network topology in distributed systems"}]})
        update_article(session, article, status="published", published_at=datetime.utcnow())

        response = client.get("/api/articles/search?q=distributed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Networking Guide"

    def test_search_excludes_drafts(self, client: TestClient, session):
        from app.services.article_service import create_article

        create_article(session, "Draft Docker", {"type": "doc", "content": [{"type": "text", "text": "Docker deep dive"}]})

        response = client.get("/api/articles/search?q=docker")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_search_returns_400_when_q_missing(self, client: TestClient):
        response = client.get("/api/articles/search")
        assert response.status_code == 400
        assert "q" in response.json()["detail"].lower() or "query" in response.json()["detail"].lower()

    def test_search_returns_400_when_q_empty(self, client: TestClient):
        response = client.get("/api/articles/search?q=")
        assert response.status_code == 400

    def test_search_ranks_title_match_above_content_match(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        title_match = create_article(session, "Docker Best Practices", {"type": "doc", "content": [{"type": "text", "text": "General devops tips"}]})
        update_article(session, title_match, status="published", published_at=datetime.utcnow())

        content_match = create_article(session, "DevOps Overview", {"type": "doc", "content": [{"type": "text", "text": "Docker containers explained in depth"}]})
        update_article(session, content_match, status="published", published_at=datetime.utcnow())

        response = client.get("/api/articles/search?q=docker")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Docker Best Practices"
        assert data[1]["title"] == "DevOps Overview"

    def test_search_is_case_insensitive(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        article = create_article(session, "Vue 3 Composition API", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.utcnow())

        response = client.get("/api/articles/search?q=VUE")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Vue 3 Composition API"

    def test_search_returns_empty_list_when_no_matches(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        article = create_article(session, "Python Tips", {"type": "doc"})
        update_article(session, article, status="published", published_at=datetime.utcnow())

        response = client.get("/api/articles/search?q=kubernetes")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_search_finds_by_tag_name(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        article = create_article(
            session, "Hidden Gem", {"type": "doc", "content": [{"type": "text", "text": "Some content"}]},
            tag_names=["kubernetes"]
        )
        update_article(session, article, status="published", published_at=datetime.utcnow())

        response = client.get("/api/articles/search?q=kubernetes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Hidden Gem"

    def test_search_tag_match_ranks_below_title_match(self, client: TestClient, session):
        from app.services.article_service import create_article, update_article
        from datetime import datetime

        title_match = create_article(
            session, "Kubernetes Guide", {"type": "doc", "content": [{"type": "text", "text": "Other content"}]}
        )
        update_article(session, title_match, status="published", published_at=datetime.utcnow())

        tag_match = create_article(
            session, "Container Basics", {"type": "doc", "content": [{"type": "text", "text": "Docker intro"}]},
            tag_names=["kubernetes"]
        )
        update_article(session, tag_match, status="published", published_at=datetime.utcnow())

        response = client.get("/api/articles/search?q=kubernetes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Kubernetes Guide"
        assert data[1]["title"] == "Container Basics"
