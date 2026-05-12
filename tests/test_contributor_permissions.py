import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User
from app.services.auth_service import create_access_token, get_password_hash


def _create_user_token(session: Session, email: str, role: str, is_active: bool = True, is_verified: bool = True) -> dict:
    """Create a user and return auth headers."""
    user = User(
        email=email,
        hashed_password=get_password_hash("password123"),
        role=role,
        is_active=is_active,
        is_verified=is_verified,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
    return {"Authorization": f"Bearer {token}"}


class TestContributorArticlePermissions:
    """Integration tests for contributor role permissions on articles."""

    def test_contributor_can_create_article(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor@test.com", "contributor")
        response = client.post(
            "/api/admin/articles",
            json={"title": "Contributor Article", "content": {"type": "doc"}, "send_newsletter": False},
            headers=contributor_token,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Contributor Article"
        assert data["status"] == "draft"

    def test_contributor_can_edit_own_article(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor2@test.com", "contributor")
        user = session.exec(select(User).where(User.email == "contributor2@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "Own Article", {"type": "doc"}, author_id=user.id)
        
        response = client.put(
            f"/api/articles/{article.id}",
            json={"title": "Updated Title"},
            headers=contributor_token,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_contributor_cannot_edit_others_article(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor3@test.com", "contributor")
        other_token = _create_user_token(session, "other@test.com", "contributor")
        other_user = session.exec(select(User).where(User.email == "other@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "Other's Article", {"type": "doc"}, author_id=other_user.id)
        
        response = client.put(
            f"/api/articles/{article.id}",
            json={"title": "Hacked Title"},
            headers=contributor_token,
        )
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_contributor_cannot_publish_own_article(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor4@test.com", "contributor")
        user = session.exec(select(User).where(User.email == "contributor4@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "Unpublished", {"type": "doc"}, author_id=user.id)
        
        response = client.put(
            f"/api/articles/{article.id}",
            json={"status": "published"},
            headers=contributor_token,
        )
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_contributor_cannot_delete_own_article(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor5@test.com", "contributor")
        user = session.exec(select(User).where(User.email == "contributor5@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "To Delete", {"type": "doc"}, author_id=user.id)
        
        response = client.delete(f"/api/articles/{article.id}", headers=contributor_token)
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_contributor_cannot_delete_others_article(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor6@test.com", "contributor")
        other_token = _create_user_token(session, "other2@test.com", "contributor")
        other_user = session.exec(select(User).where(User.email == "other2@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "Other's Delete", {"type": "doc"}, author_id=other_user.id)
        
        response = client.delete(f"/api/articles/{article.id}", headers=contributor_token)
        assert response.status_code == 403

    def test_contributor_can_autosave_own_article(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor7@test.com", "contributor")
        user = session.exec(select(User).where(User.email == "contributor7@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "Autosave Test", {"type": "doc"}, author_id=user.id)
        
        response = client.put(
            f"/api/admin/articles/{article.id}/autosave",
            json={"title": "Autosaved", "content": {"type": "doc"}},
            headers=contributor_token,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Autosaved"

    def test_contributor_cannot_autosave_others_article(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor8@test.com", "contributor")
        other_user = session.exec(select(User).where(User.email == "other3@test.com")).first()
        if other_user is None:
            other_user = User(
                email="other3@test.com",
                hashed_password=get_password_hash("password123"),
                role="contributor",
                is_active=True,
                is_verified=True,
            )
            session.add(other_user)
            session.commit()
            session.refresh(other_user)
        
        from app.services.article_service import create_article
        article = create_article(session, "Other's Autosave", {"type": "doc"}, author_id=other_user.id)
        
        response = client.put(
            f"/api/admin/articles/{article.id}/autosave",
            json={"title": "Hacked", "content": {"type": "doc"}},
            headers=contributor_token,
        )
        assert response.status_code == 403

    def test_editor_can_edit_any_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor9@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor9@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "Contributor's Article", {"type": "doc"}, author_id=contributor.id)
        
        response = client.put(
            f"/api/articles/{article.id}",
            json={"title": "Editor Updated"},
            headers=editor_token,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Editor Updated"

    def test_editor_can_delete_any_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor2@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor10@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor10@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "Editor Delete Test", {"type": "doc"}, author_id=contributor.id)
        
        response = client.delete(f"/api/articles/{article.id}", headers=editor_token)
        assert response.status_code == 204

    def test_admin_can_edit_any_article(self, client: TestClient, session: Session):
        admin_token = _create_user_token(session, "admin2@test.com", "admin")
        contributor_token = _create_user_token(session, "contributor11@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor11@test.com")).first()
        
        from app.services.article_service import create_article
        article = create_article(session, "Admin Edit Test", {"type": "doc"}, author_id=contributor.id)
        
        response = client.put(
            f"/api/articles/{article.id}",
            json={"title": "Admin Updated"},
            headers=admin_token,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Admin Updated"
