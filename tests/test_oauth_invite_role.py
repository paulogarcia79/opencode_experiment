import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User
from app.services.auth_service import create_access_token, get_password_hash
from app.services.user_management_service import complete_setup, generate_setup_token
from app.config import settings


def create_user(session: Session, email: str, role: str = "contributor", is_verified: bool = True) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash("testpassword"),
        role=role,
        is_active=True,
        is_verified=is_verified,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_token_headers(user: User) -> dict:
    token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
    return {"Authorization": f"Bearer {token}"}


def test_send_invite_email_url_format():
    """send_invite_email uses /auth?setup=TOKEN URL format."""
    from app.services.email_service import send_invite_email

    with patch("app.services.email_service.settings") as mock_settings, \
         patch("app.services.email_service.render") as mock_render, \
         patch("app.services.email_service._process_cids") as mock_cids, \
         patch("app.services.email_service.resend") as mock_resend:
        mock_settings.RESEND_API_KEY = "key123"
        mock_settings.RESEND_FROM_EMAIL = "from@test.com"
        mock_settings.APP_BASE_URL = "http://localhost:5173"
        mock_settings.SITE_NAME = "Test Site"
        mock_render.return_value = "<html></html>"
        mock_cids.return_value = ("<html></html>", None)

        send_invite_email("invite@example.com", "abc-token-123", role="editor")

        mock_render.assert_called_once()
        context = mock_render.call_args[0][1]
        assert context["setup_url"] == "http://localhost:5173/auth?setup=abc-token-123"


def test_invite_existing_user_overwrites_role(client: TestClient, session: Session):
    """Admin inviting an existing self-registered contributor updates their role."""
    from unittest.mock import patch
    from app.routers import users as users_router

    users_router._invite_cooldown.clear()

    user = create_user(session, "invite-existing@example.com", role="contributor")
    assert user.role == "contributor"

    # Create an admin to make the request
    admin = create_user(session, "admin-inviter@example.com", role="admin")
    admin_headers = get_token_headers(admin)

    with patch("app.routers.users.send_invite_email") as mock_send:
        response = client.post(
            "/api/admin/users/invite",
            json={"email": "invite-existing@example.com", "role": "editor"},
            headers=admin_headers,
        )
    assert response.status_code == 200

    # Refresh user from DB
    session.refresh(user)

    # Role should be updated to invited role
    assert user.role == "editor"
    # Setup token should be set for password setup
    assert user.setup_token_hash is not None


def test_complete_setup_keeps_invited_role(client: TestClient, session: Session):
    """After invite sets role to editor, setup completion keeps editor role."""
    from app.routers import users as users_router

    users_router._invite_cooldown.clear()

    user = create_user(session, "setup-role@example.com", role="contributor")
    admin = create_user(session, "admin-role@example.com", role="admin")
    admin_headers = get_token_headers(admin)

    with patch("app.routers.users.send_invite_email"):
        client.post(
            "/api/admin/users/invite",
            json={"email": "setup-role@example.com", "role": "editor"},
            headers=admin_headers,
        )

    session.refresh(user)
    assert user.role == "editor"

    # Complete setup via the endpoint (simulates password creation)
    # Generate a fresh setup token to get the plaintext
    plaintext = generate_setup_token(user, session)

    client.post("/api/auth/setup", json={"token": plaintext, "password": "NewSecurePass1"})

    session.refresh(user)
    assert user.role == "editor"
    assert user.is_verified is True
