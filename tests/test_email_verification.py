import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.services.auth_service import pwd_context


class TestVerifyEmail:
    """Test email verification endpoint."""

    def test_verify_email_success(self, client: TestClient, session: Session):
        """Valid verification token sets is_verified=True and returns JWT."""
        user = User(
            email="unverified@example.com",
            hashed_password="some-hash",
            is_verified=False,
        )
        plaintext = "test-verification-token"
        user.verification_token_hash = pwd_context.hash(plaintext)
        user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        session.add(user)
        session.commit()

        response = client.post(
            "/api/auth/verify-email",
            json={"token": plaintext},
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["type"] == "bearer"

        session.refresh(user)
        assert user.is_verified is True
        assert user.verification_token_hash is None

    def test_verify_email_invalid_token(self, client: TestClient, session: Session):
        """Invalid verification token returns 400."""
        response = client.post(
            "/api/auth/verify-email",
            json={"token": "invalid-token"},
        )
        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]

    def test_verify_email_expired_token(self, client: TestClient, session: Session):
        """Expired verification token returns 400."""
        user = User(
            email="expired@example.com",
            hashed_password="some-hash",
            is_verified=False,
        )
        plaintext = "expired-token"
        user.verification_token_hash = pwd_context.hash(plaintext)
        user.verification_token_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        session.add(user)
        session.commit()

        response = client.post(
            "/api/auth/verify-email",
            json={"token": plaintext},
        )
        assert response.status_code == 400

    def test_verify_email_already_verified(self, client: TestClient, session: Session):
        """Already verified user returns 400."""
        user = User(
            email="verified@example.com",
            hashed_password="some-hash",
            is_verified=True,
        )
        plaintext = "already-verified-token"
        user.verification_token_hash = pwd_context.hash(plaintext)
        user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        session.add(user)
        session.commit()

        response = client.post(
            "/api/auth/verify-email",
            json={"token": plaintext},
        )
        assert response.status_code == 400


class TestResendVerification:
    """Test resend verification endpoint."""

    def test_resend_verification_success(self, client: TestClient, session: Session):
        """Resend verification sends email for unverified user."""
        from unittest.mock import patch
        from app.routers import auth as auth_router
        from app.services.auth_service import get_password_hash, create_access_token

        auth_router._verification_cooldown.clear()

        user = User(
            email="resend@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_verified=False,
            role="contributor",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
        headers = {"Authorization": f"Bearer {token}"}

        with patch("app.routers.auth.send_verification_email") as mock_send:
            response = client.post(
                "/api/auth/resend-verification",
                headers=headers,
            )
            assert response.status_code == 200
            mock_send.assert_called_once()

    def test_resend_verification_verified_user(self, client: TestClient, session: Session):
        """Resend for already verified user still sends (regenerate if needed)."""
        from unittest.mock import patch
        from app.routers import auth as auth_router
        from app.services.auth_service import get_password_hash, create_access_token

        auth_router._verification_cooldown.clear()

        user = User(
            email="already-verified@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_verified=True,
            role="contributor",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
        headers = {"Authorization": f"Bearer {token}"}

        with patch("app.routers.auth.send_verification_email") as mock_send:
            response = client.post(
                "/api/auth/resend-verification",
                headers=headers,
            )
            assert response.status_code == 200
            mock_send.assert_called_once()

    def test_resend_verification_unauthenticated(self, client: TestClient):
        """Resend without Bearer token returns 401."""
        response = client.post("/api/auth/resend-verification")
        assert response.status_code == 401

    def test_resend_verification_cooldown(self, client: TestClient, session: Session):
        """Rapid resend requests are rate-limited."""
        from unittest.mock import patch
        from app.routers import auth as auth_router
        from app.services.auth_service import get_password_hash, create_access_token

        auth_router._verification_cooldown.clear()

        user = User(
            email="cooldown@example.com",
            hashed_password=get_password_hash("testpassword"),
            is_verified=False,
            role="contributor",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
        headers = {"Authorization": f"Bearer {token}"}

        with patch("app.routers.auth.send_verification_email"):
            response1 = client.post(
                "/api/auth/resend-verification",
                headers=headers,
            )
            assert response1.status_code == 200

            response2 = client.post(
                "/api/auth/resend-verification",
                headers=headers,
            )
            assert response2.status_code == 429


class TestRequireAdminUnverified:
    """Test that require_admin rejects unverified users."""

    def test_unverified_user_rejected(self, client: TestClient, session: Session, admin_token: dict):
        """Unverified user cannot access admin endpoints."""
        from app.models.user import User
        from app.services.auth_service import create_access_token

        user = session.exec(select(User)).first()
        user.is_verified = False
        session.add(user)
        session.commit()

        new_token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
        headers = {"Authorization": f"Bearer {new_token}"}

        response = client.get("/api/admin/articles", headers=headers)
        assert response.status_code == 403

    def test_verified_user_allowed(self, client: TestClient, admin_token: dict):
        """Verified user can access admin endpoints."""
        response = client.get("/api/admin/articles", headers=admin_token)
        assert response.status_code == 200
