import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User
from app.models import Article
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


class TestEditorArticlePermissions:
    """Integration tests for editor role permissions on articles."""

    def test_editor_can_create_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-create@test.com", "editor")
        response = client.post(
            "/api/admin/articles",
            json={"title": "Editor Article", "content": {"type": "doc"}, "send_newsletter": False},
            headers=editor_token,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Editor Article"
        assert data["status"] == "draft"

    def test_editor_can_list_articles(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-list@test.com", "editor")
        response = client.get("/api/admin/articles", headers=editor_token)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_editor_can_get_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-get@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor-for-get@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor-for-get@test.com")).first()
        article = create_article(session, "Get Test", {"type": "doc"}, author_id=contributor.id)

        response = client.get(f"/api/admin/articles/{article.id}", headers=editor_token)
        assert response.status_code == 200
        assert response.json()["title"] == "Get Test"

    def test_editor_can_edit_any_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-edit@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor-for-edit@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor-for-edit@test.com")).first()
        article = create_article(session, "Original Title", {"type": "doc"}, author_id=contributor.id)

        response = client.put(
            f"/api/articles/{article.id}",
            json={"title": "Editor Updated"},
            headers=editor_token,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Editor Updated"

    def test_editor_can_publish_any_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-publish@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor-for-publish@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor-for-publish@test.com")).first()
        article = create_article(session, "Unpublished Article", {"type": "doc"}, author_id=contributor.id)

        response = client.put(
            f"/api/articles/{article.id}",
            json={"status": "published"},
            headers=editor_token,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "published"

    def test_editor_can_delete_any_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-delete@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor-for-delete@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor-for-delete@test.com")).first()
        article = create_article(session, "To Be Deleted", {"type": "doc"}, author_id=contributor.id)

        response = client.delete(f"/api/articles/{article.id}", headers=editor_token)
        assert response.status_code == 204

    def test_editor_can_autosave_any_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-autosave@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor-for-autosave@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor-for-autosave@test.com")).first()
        article = create_article(session, "Autosave Target", {"type": "doc"}, author_id=contributor.id)

        response = client.put(
            f"/api/admin/articles/{article.id}/autosave",
            json={"title": "Autosaved by Editor", "content": {"type": "doc"}},
            headers=editor_token,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Autosaved by Editor"


class TestEditorTagPermissions:
    """Integration tests for editor role permissions on tags."""

    def test_editor_can_list_tags(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-tags@test.com", "editor")
        response = client.get("/api/admin/tags", headers=editor_token)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_editor_can_delete_tag(self, client: TestClient, session: Session):
        from app.models.tag import Tag
        editor_token = _create_user_token(session, "editor-delete-tag@test.com", "editor")
        tag = Tag(name="TestTag", slug="test-tag")
        session.add(tag)
        session.commit()

        response = client.delete(f"/api/admin/tags/{tag.id}", headers=editor_token)
        assert response.status_code == 204


class TestEditorImportPermissions:
    """Integration tests for editor role permissions on markdown import."""

    def test_editor_can_access_import_endpoint(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-import@test.com", "editor")
        # Send empty file list - will fail with 422 for missing files, but not 403
        response = client.post("/api/admin/articles/import", headers=editor_token)
        # 422 means endpoint is accessible (validation error), 403 would mean blocked
        assert response.status_code != 403


class TestEditorImagePermissions:
    """Integration tests for editor role permissions on images."""

    def test_editor_can_list_images(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-images@test.com", "editor")
        response = client.get("/api/admin/images", headers=editor_token)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestEditorAnalyticsPermissions:
    """Integration tests for editor role permissions on analytics."""

    def test_editor_can_access_analytics(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-analytics@test.com", "editor")
        response = client.get("/api/admin/analytics", headers=editor_token)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data


class TestEditorRevisionPermissions:
    """Integration tests for editor role permissions on revisions."""

    def test_editor_can_list_revisions(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-revisions@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor-for-revisions@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor-for-revisions@test.com")).first()
        article = create_article(session, "Revision Test", {"type": "doc"}, author_id=contributor.id)

        response = client.get(f"/api/admin/articles/{article.id}/revisions", headers=editor_token)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_editor_can_get_revision(self, client: TestClient, session: Session):
        from app.services.revision_service import create_revision
        editor_token = _create_user_token(session, "editor-get-rev@test.com", "editor")
        editor = session.exec(select(User).where(User.email == "editor-get-rev@test.com")).first()
        article = create_article(session, "Revision Get Test", {"type": "doc"}, author_id=editor.id)
        create_revision(session, article, "save", author_id=editor.id)

        response = client.get(f"/api/admin/articles/{article.id}/revisions/1", headers=editor_token)
        assert response.status_code == 200

    def test_editor_can_restore_revision(self, client: TestClient, session: Session):
        from app.services.revision_service import create_revision
        editor_token = _create_user_token(session, "editor-restore-rev@test.com", "editor")
        editor = session.exec(select(User).where(User.email == "editor-restore-rev@test.com")).first()
        article = create_article(session, "Restore Test", {"type": "doc"}, author_id=editor.id)
        create_revision(session, article, "save", author_id=editor.id)

        response = client.post(
            f"/api/admin/articles/{article.id}/revisions/1/restore",
            headers=editor_token,
        )
        assert response.status_code == 200


class TestEditorPreviewPermissions:
    """Integration tests for editor role permissions on preview email."""

    def test_editor_can_preview_email(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-preview@test.com", "editor")
        editor = session.exec(select(User).where(User.email == "editor-preview@test.com")).first()
        article = create_article(session, "Preview Test", {"type": "doc"}, author_id=editor.id)

        response = client.post(
            f"/api/admin/articles/{article.id}/preview-email",
            headers=editor_token,
        )
        # Will fail if no email service configured, but should not be 403
        assert response.status_code != 403


class TestEditorBlockedPermissions:
    """Integration tests for editor role blocked permissions."""

    def test_editor_cannot_access_users_list(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-blocked-users@test.com", "editor")
        response = client.get("/api/admin/users/", headers=editor_token)
        assert response.status_code == 403

    def test_editor_cannot_invite_user(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-blocked-invite@test.com", "editor")
        response = client.post(
            "/api/admin/users/invite",
            json={"email": "newuser@test.com", "role": "contributor"},
            headers=editor_token,
        )
        assert response.status_code == 403

    def test_editor_cannot_update_user_role(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-blocked-role@test.com", "editor")
        admin = session.exec(select(User).where(User.email == "admin@example.com")).first()
        if admin is None:
            admin_token = _create_user_token(session, "temp-admin@test.com", "admin")
            admin = session.exec(select(User).where(User.email == "temp-admin@test.com")).first()

        response = client.put(
            f"/api/admin/users/{admin.id}/role",
            json={"role": "editor"},
            headers=editor_token,
        )
        assert response.status_code == 403

    def test_editor_cannot_toggle_user_active(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-blocked-active@test.com", "editor")
        admin_token = _create_user_token(session, "temp-admin-active@test.com", "admin")
        admin = session.exec(select(User).where(User.email == "temp-admin-active@test.com")).first()

        response = client.put(
            f"/api/admin/users/{admin.id}/active",
            json={"is_active": False},
            headers=editor_token,
        )
        assert response.status_code == 403

    def test_editor_cannot_reassign_article(self, client: TestClient, session: Session):
        editor_token = _create_user_token(session, "editor-blocked-reassign@test.com", "editor")
        contributor_token = _create_user_token(session, "contributor-for-reassign@test.com", "contributor")
        contributor = session.exec(select(User).where(User.email == "contributor-for-reassign@test.com")).first()
        article = create_article(session, "Reassign Test", {"type": "doc"}, author_id=contributor.id)

        editor = session.exec(select(User).where(User.email == "editor-blocked-reassign@test.com")).first()
        response = client.put(
            f"/api/admin/articles/{article.id}/reassign",
            json={"author_id": str(editor.id)},
            headers=editor_token,
        )
        assert response.status_code == 403
