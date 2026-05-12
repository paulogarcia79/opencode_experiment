import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User
from app.models.article import Article
from app.models.article_revision import ArticleRevision
from app.services.auth_service import create_access_token, get_password_hash
from app.services.article_service import create_article


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


class TestArticleReassignment:
    """Integration tests for article reassignment endpoint."""

    def test_admin_can_reassign_article(self, client: TestClient, session: Session):
        admin_token = _create_user_token(session, "admin_reassign@test.com", "admin")
        new_author_token = _create_user_token(session, "new_author@test.com", "editor")
        new_author = session.exec(select(User).where(User.email == "new_author@test.com")).first()

        article = create_article(session, "Reassign Test", {"type": "doc"}, author_id=None)

        response = client.put(
            f"/api/admin/articles/{article.id}/reassign",
            json={"author_id": str(new_author.id)},
            headers=admin_token,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["author"]["id"] == str(new_author.id)
        assert data["author"]["email"] == "new_author@test.com"

        # Verify article author was updated
        session.refresh(article)
        assert str(article.author_id) == str(new_author.id)

    def test_reassign_creates_revision(self, client: TestClient, session: Session):
        admin_token = _create_user_token(session, "admin_rev@test.com", "admin")
        new_author_token = _create_user_token(session, "new_author_rev@test.com", "editor")
        new_author = session.exec(select(User).where(User.email == "new_author_rev@test.com")).first()

        article = create_article(session, "Revision Test", {"type": "doc"}, author_id=None)

        response = client.put(
            f"/api/admin/articles/{article.id}/reassign",
            json={"author_id": str(new_author.id)},
            headers=admin_token,
        )
        assert response.status_code == 200

        # Verify revision was created
        revisions = session.exec(
            select(ArticleRevision)
            .where(ArticleRevision.article_id == article.id)
            .where(ArticleRevision.change_type == "reassign")
        ).all()
        assert len(revisions) == 1
        revision = revisions[0]
        assert revision.change_type == "reassign"
        assert revision.reassign_metadata["old_author_id"] is None
        assert revision.reassign_metadata["new_author_id"] == str(new_author.id)

    def test_reassign_returns_404_if_article_not_found(self, client: TestClient, session: Session):
        admin_token = _create_user_token(session, "admin_404@test.com", "admin")
        new_author_token = _create_user_token(session, "new_author_404@test.com", "editor")
        new_author = session.exec(select(User).where(User.email == "new_author_404@test.com")).first()

        import uuid
        fake_id = uuid.uuid4()

        response = client.put(
            f"/api/admin/articles/{fake_id}/reassign",
            json={"author_id": str(new_author.id)},
            headers=admin_token,
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_reassign_returns_403_for_contributor(self, client: TestClient, session: Session):
        contributor_token = _create_user_token(session, "contributor_reassign@test.com", "contributor")
        new_author_token = _create_user_token(session, "new_author_contrib@test.com", "editor")
        new_author = session.exec(select(User).where(User.email == "new_author_contrib@test.com")).first()

        article = create_article(session, "Contributor Reassign", {"type": "doc"}, author_id=None)

        response = client.put(
            f"/api/admin/articles/{article.id}/reassign",
            json={"author_id": str(new_author.id)},
            headers=contributor_token,
        )
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_reassign_returns_400_if_target_user_not_found(self, client: TestClient, session: Session):
        admin_token = _create_user_token(session, "admin_400@test.com", "admin")

        article = create_article(session, "Bad Reassign", {"type": "doc"}, author_id=None)

        import uuid
        fake_user_id = uuid.uuid4()

        response = client.put(
            f"/api/admin/articles/{article.id}/reassign",
            json={"author_id": str(fake_user_id)},
            headers=admin_token,
        )
        assert response.status_code == 400
        assert "user" in response.json()["detail"].lower()

    def test_reassign_returns_400_if_target_user_inactive(self, client: TestClient, session: Session):
        admin_token = _create_user_token(session, "admin_inactive@test.com", "admin")
        inactive_user = User(
            email="inactive@test.com",
            hashed_password=get_password_hash("password123"),
            role="editor",
            is_active=False,
            is_verified=True,
        )
        session.add(inactive_user)
        session.commit()
        session.refresh(inactive_user)

        article = create_article(session, "Inactive Reassign", {"type": "doc"}, author_id=None)

        response = client.put(
            f"/api/admin/articles/{article.id}/reassign",
            json={"author_id": str(inactive_user.id)},
            headers=admin_token,
        )
        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()

    def test_editor_can_reassign_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor_reassign@test.com", "editor")
        new_author_token = _create_user_token(session, "new_author_editor@test.com", "admin")
        new_author = session.exec(select(User).where(User.email == "new_author_editor@test.com")).first()

        article = create_article(session, "Editor Reassign", {"type": "doc"}, author_id=None)

        response = client.put(
            f"/api/admin/articles/{article.id}/reassign",
            json={"author_id": str(new_author.id)},
            headers=editor_token,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["author"]["id"] == str(new_author.id)

    def test_reassign_with_existing_author(self, client: TestClient, session: Session):
        admin_token = _create_user_token(session, "admin_existing@test.com", "admin")
        old_author_token = _create_user_token(session, "old_author@test.com", "contributor")
        old_author = session.exec(select(User).where(User.email == "old_author@test.com")).first()
        new_author_token = _create_user_token(session, "new_author_existing@test.com", "editor")
        new_author = session.exec(select(User).where(User.email == "new_author_existing@test.com")).first()

        article = create_article(session, "Existing Author", {"type": "doc"}, author_id=old_author.id)

        response = client.put(
            f"/api/admin/articles/{article.id}/reassign",
            json={"author_id": str(new_author.id)},
            headers=admin_token,
        )
        assert response.status_code == 200

        # Verify revision captured old author
        revision = session.exec(
            select(ArticleRevision)
            .where(ArticleRevision.article_id == article.id)
            .where(ArticleRevision.change_type == "reassign")
        ).first()
        assert revision.reassign_metadata["old_author_id"] == str(old_author.id)
        assert revision.reassign_metadata["new_author_id"] == str(new_author.id)
