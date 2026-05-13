import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import User
from app.services.auth_service import create_access_token, get_password_hash


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


def test_send_verification_email_passes_role_and_url():
    """send_verification_email passes role to template and uses frontend URL format."""
    from app.services.email_service import send_verification_email

    with patch("app.services.email_service.settings") as mock_settings, \
         patch("app.services.email_service.render") as mock_render, \
         patch("app.services.email_service._process_cids") as mock_cids, \
         patch("app.services.email_service.resend") as mock_resend:
        mock_settings.RESEND_API_KEY = "key123"
        mock_settings.RESEND_FROM_EMAIL = "from@test.com"
        mock_settings.APP_BASE_URL = "http://localhost:5173"
        mock_render.return_value = "<html></html>"
        mock_cids.return_value = ("<html></html>", None)

        send_verification_email("test@example.com", "abc123", role="contributor")

        # Verify render was called with correct context
        mock_render.assert_called_once()
        call_args = mock_render.call_args
        template_name = call_args[0][0]
        context = call_args[0][1]

        assert template_name == "email_verification.mjml"
        assert context["role"] == "contributor"
        assert context["verification_url"] == "http://localhost:5173/verify-email?token=abc123"


def test_resend_verification_requires_bearer(client: TestClient):
    """POST /api/auth/resend-verification without Bearer token returns 401."""
    response = client.post("/api/auth/resend-verification", json={"email": "test@example.com"})
    assert response.status_code == 401


def test_resend_verification_bearer_works(client: TestClient, session: Session):
    """POST /api/auth/resend-verification with valid Bearer token sends email."""
    from app.routers.auth import _verification_cooldown
    _verification_cooldown.clear()

    user = create_user(session, "resend-test@example.com", is_verified=False)
    headers = get_token_headers(user)

    with patch("app.routers.auth.send_verification_email") as mock_send:
        response = client.post("/api/auth/resend-verification", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "verification link has been sent" in data["message"]
    mock_send.assert_called_once()
    args = mock_send.call_args
    assert args[0][0] == "resend-test@example.com"
    assert args[1]["role"] == "contributor"


def test_resend_verification_cooldown(client: TestClient, session: Session):
    """Resend verification enforces 60-second cooldown."""
    from app.routers.auth import _verification_cooldown
    _verification_cooldown.clear()

    user = create_user(session, "cooldown-test@example.com", is_verified=False)
    headers = get_token_headers(user)

    with patch("app.routers.auth.send_verification_email"):
        response1 = client.post("/api/auth/resend-verification", headers=headers)
        assert response1.status_code == 200

        response2 = client.post("/api/auth/resend-verification", headers=headers)
        assert response2.status_code == 429
