import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User
from tests.conftest import create_user, create_user_token, get_token_for_user


def _get_admin(session: Session) -> User:
    return session.exec(select(User)).first()


class TestListUsers:
    def test_list_users_requires_admin(self, client: TestClient, session: Session):
        editor = create_user(session, "editor@example.com", role="editor")
        headers = get_token_for_user(editor)

        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 403

    def test_list_users_returns_all_users(self, client: TestClient, session: Session):
        admin = _get_admin(session)
        create_user(session, "user1@example.com", role="editor")
        create_user(session, "user2@example.com", role="contributor")

        headers = get_token_for_user(admin)
        response = client.get("/api/admin/users", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        emails = {u["email"] for u in data}
        assert admin.email in emails
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails

    def test_list_users_returns_correct_fields(self, client: TestClient, session: Session):
        admin = _get_admin(session)
        headers = get_token_for_user(admin)

        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        user = data[0]
        assert "id" in user
        assert "email" in user
        assert "role" in user
        assert "is_active" in user
        assert "is_verified" in user
        assert "created_at" in user


class TestInviteUser:
    def test_invite_user_requires_admin(self, client: TestClient, session: Session):
        editor = create_user(session, "editor@example.com", role="editor")
        headers = get_token_for_user(editor)

        response = client.post("/api/admin/users/invite", headers=headers, json={"email": "new@example.com", "role": "contributor"})
        assert response.status_code == 403

    def test_invite_user_creates_user_and_sends_email(self, client: TestClient, session: Session, arq_pool):
        from unittest.mock import patch
        from app.routers.users import _invite_cooldown

        _invite_cooldown.clear()
        admin = _get_admin(session)
        headers = get_token_for_user(admin)

        with patch("app.routers.users.send_invite_email") as mock_send:
            response = client.post(
                "/api/admin/users/invite",
                headers=headers,
                json={"email": "newuser@example.com", "role": "editor"}
            )

        assert response.status_code == 200
        data = response.json()
        assert "invite sent" in data["message"].lower()

        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args[0][0] == "newuser@example.com"

        created_user = session.exec(select(User).where(User.email == "newuser@example.com")).first()
        assert created_user is not None
        assert created_user.role == "editor"
        assert created_user.is_verified is False
        assert created_user.setup_token_hash is not None

    def test_invite_existing_user_succeeds(self, client: TestClient, session: Session):
        """Inviting an existing user updates their role and sends setup email."""
        from unittest.mock import patch
        from app.routers.users import _invite_cooldown
        _invite_cooldown.clear()

        admin = _get_admin(session)
        headers = get_token_for_user(admin)
        existing = create_user(session, "existing@example.com", role="contributor")

        with patch("app.routers.users.send_invite_email") as mock_send:
            response = client.post(
                "/api/admin/users/invite",
                headers=headers,
                json={"email": "existing@example.com", "role": "editor"}
            )
            assert response.status_code == 200
            mock_send.assert_called_once()

        # Existing user's role should be updated
        session.refresh(existing)
        assert existing.role == "editor"
        assert existing.setup_token_hash is not None

    def test_invite_user_cooldown(self, client: TestClient, session: Session):
        from unittest.mock import patch
        from app.routers.users import _invite_cooldown

        _invite_cooldown.clear()
        admin = _get_admin(session)
        headers = get_token_for_user(admin)

        with patch("app.routers.users.send_invite_email"):
            response1 = client.post(
                "/api/admin/users/invite",
                headers=headers,
                json={"email": "user@example.com", "role": "contributor"}
            )
            assert response1.status_code == 200

            response2 = client.post(
                "/api/admin/users/invite",
                headers=headers,
                json={"email": "user@example.com", "role": "contributor"}
            )
            assert response2.status_code == 429


class TestUpdateUserRole:
    def test_update_role_requires_admin(self, client: TestClient, session: Session):
        editor = create_user(session, "editor@example.com", role="editor")
        contributor = create_user(session, "contributor@example.com", role="contributor")
        headers = get_token_for_user(editor)

        response = client.put(f"/api/admin/users/{contributor.id}/role", headers=headers, json={"role": "editor"})
        assert response.status_code == 403

    def test_update_role_success(self, client: TestClient, session: Session):
        admin = _get_admin(session)
        user = create_user(session, "user@example.com", role="contributor")
        headers = get_token_for_user(admin)

        response = client.put(f"/api/admin/users/{user.id}/role", headers=headers, json={"role": "editor"})
        assert response.status_code == 200

        session.refresh(user)
        assert user.role == "editor"

    def test_update_role_invalid_role_returns_400(self, client: TestClient, session: Session):
        admin = _get_admin(session)
        user = create_user(session, "user@example.com", role="contributor")
        headers = get_token_for_user(admin)

        response = client.put(f"/api/admin/users/{user.id}/role", headers=headers, json={"role": "superadmin"})
        assert response.status_code == 400

    def test_update_role_user_not_found_returns_404(self, client: TestClient, session: Session):
        admin = _get_admin(session)
        headers = get_token_for_user(admin)

        response = client.put("/api/admin/users/00000000-0000-0000-0000-000000000000/role", headers=headers, json={"role": "editor"})
        assert response.status_code == 404


class TestToggleUserActive:
    def test_toggle_active_requires_admin(self, client: TestClient, session: Session):
        editor = create_user(session, "editor@example.com", role="editor")
        headers = get_token_for_user(editor)

        response = client.put(f"/api/admin/users/{editor.id}/active", headers=headers, json={"is_active": False})
        assert response.status_code == 403

    def test_deactivate_user(self, client: TestClient, session: Session):
        admin = _get_admin(session)
        user = create_user(session, "user@example.com", role="contributor")
        headers = get_token_for_user(admin)

        response = client.put(f"/api/admin/users/{user.id}/active", headers=headers, json={"is_active": False})
        assert response.status_code == 200

        session.refresh(user)
        assert user.is_active is False

    def test_reactivate_user(self, client: TestClient, session: Session):
        admin = _get_admin(session)
        user = create_user(session, "user@example.com", role="contributor", is_active=False)
        headers = get_token_for_user(admin)

        response = client.put(f"/api/admin/users/{user.id}/active", headers=headers, json={"is_active": True})
        assert response.status_code == 200

        session.refresh(user)
        assert user.is_active is True

    def test_toggle_active_user_not_found_returns_404(self, client: TestClient, session: Session):
        admin = _get_admin(session)
        headers = get_token_for_user(admin)

        response = client.put("/api/admin/users/00000000-0000-0000-0000-000000000000/active", headers=headers, json={"is_active": False})
        assert response.status_code == 404


class TestSetupEndpoint:
    def test_setup_with_valid_token(self, client: TestClient, session: Session):
        from app.services.auth_service import pwd_context
        import secrets

        user = create_user(session, "newuser@example.com", role="contributor", is_verified=False)
        plaintext = secrets.token_urlsafe(32)
        hashed = pwd_context.hash(plaintext)
        user.setup_token_hash = hashed
        from datetime import datetime, timedelta, timezone
        user.setup_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        session.add(user)
        session.commit()

        response = client.post(
            "/api/auth/setup",
            json={"token": plaintext, "password": "my-new-password"}
        )
        assert response.status_code == 200

        session.refresh(user)
        assert user.is_verified is True
        assert user.setup_token_hash is None
        from app.services.auth_service import verify_password
        assert verify_password("my-new-password", user.hashed_password)

    def test_setup_with_invalid_token(self, client: TestClient, session: Session):
        response = client.post(
            "/api/auth/setup",
            json={"token": "invalid-token", "password": "my-new-password"}
        )
        assert response.status_code == 400

    def test_setup_with_expired_token(self, client: TestClient, session: Session):
        from app.services.auth_service import pwd_context
        import secrets
        from datetime import datetime, timedelta, timezone

        user = create_user(session, "expired@example.com", role="contributor", is_verified=False)
        plaintext = secrets.token_urlsafe(32)
        hashed = pwd_context.hash(plaintext)
        user.setup_token_hash = hashed
        user.setup_token_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        session.add(user)
        session.commit()

        response = client.post(
            "/api/auth/setup",
            json={"token": plaintext, "password": "my-new-password"}
        )
        assert response.status_code == 400

    def test_setup_token_single_use(self, client: TestClient, session: Session):
        from app.services.auth_service import pwd_context
        import secrets
        from datetime import datetime, timedelta, timezone

        user = create_user(session, "reuse@example.com", role="contributor", is_verified=False)
        plaintext = secrets.token_urlsafe(32)
        hashed = pwd_context.hash(plaintext)
        user.setup_token_hash = hashed
        user.setup_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        session.add(user)
        session.commit()

        response1 = client.post(
            "/api/auth/setup",
            json={"token": plaintext, "password": "first-password"}
        )
        assert response1.status_code == 200

        response2 = client.post(
            "/api/auth/setup",
            json={"token": plaintext, "password": "second-password"}
        )
        assert response2.status_code == 400


class TestInactiveUserCannotLogin:
    def test_inactive_user_cannot_login(self, client: TestClient, session: Session):
        from app.services.auth_service import get_password_hash

        user = create_user(session, "inactive@example.com", role="contributor", is_active=False)
        user.hashed_password = get_password_hash("correct-password")
        session.add(user)
        session.commit()

        response = client.post(
            "/api/auth/login",
            json={"email": "inactive@example.com", "password": "correct-password"}
        )
        assert response.status_code == 401
        assert "deactivated" in response.json()["detail"].lower()
