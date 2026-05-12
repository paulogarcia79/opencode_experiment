import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User
from app.models.user_oauth_provider import UserOAuthProvider
from app.services.auth_service import create_access_token


def get_auth_headers(session: Session):
    admin = session.exec(select(User)).first()
    token = create_access_token(data={"sub": str(admin.id), "token_version": admin.token_version})
    return {"Authorization": f"Bearer {token}"}


class TestGetConnectedAccounts:
    """Test GET /api/admin/settings/accounts endpoint."""

    def test_returns_user_info_and_providers(self, client: TestClient, session: Session):
        """Should return email, is_verified, and connected providers."""
        admin = session.exec(select(User)).first()
        provider = UserOAuthProvider(user_id=admin.id, provider="google", provider_user_id="g-123")
        session.add(provider)
        session.commit()

        response = client.get("/api/admin/settings/accounts", headers=get_auth_headers(session))
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == admin.email
        assert data["is_verified"] is True
        assert len(data["connected_providers"]) == 1
        assert data["connected_providers"][0]["provider"] == "google"

    def test_returns_empty_providers(self, client: TestClient, session: Session):
        """Should return empty list when no providers connected."""
        response = client.get("/api/admin/settings/accounts", headers=get_auth_headers(session))
        assert response.status_code == 200
        data = response.json()
        assert data["connected_providers"] == []

    def test_requires_auth(self, client: TestClient):
        """Should return 401 without auth."""
        response = client.get("/api/admin/settings/accounts")
        assert response.status_code == 401


class TestDisconnectOAuth:
    """Test DELETE /api/admin/settings/accounts/oauth/{provider} endpoint."""

    def test_disconnect_google(self, client: TestClient, session: Session):
        """Should disconnect Google provider."""
        admin = session.exec(select(User)).first()
        provider = UserOAuthProvider(user_id=admin.id, provider="google", provider_user_id="g-123")
        session.add(provider)
        session.commit()

        response = client.delete("/api/admin/settings/accounts/oauth/google", headers=get_auth_headers(session))
        assert response.status_code == 200

        remaining = session.exec(
            select(UserOAuthProvider).where(UserOAuthProvider.user_id == admin.id)
        ).all()
        assert len(remaining) == 0

    def test_disconnect_not_connected_404(self, client: TestClient, session: Session):
        """Should return 404 if provider not connected."""
        response = client.delete("/api/admin/settings/accounts/oauth/google", headers=get_auth_headers(session))
        assert response.status_code == 404

    def test_disconnect_only_login_method_blocked(self, client: TestClient, session: Session):
        """Should block disconnect if it's the only login method."""
        admin = session.exec(select(User)).first()
        # Set OAuth-only marker password
        from app.services.auth_service import get_password_hash
        import secrets
        admin.hashed_password = "oauth-only:" + get_password_hash(secrets.token_urlsafe(32))
        session.add(admin)
        session.commit()

        provider = UserOAuthProvider(user_id=admin.id, provider="google", provider_user_id="g-123")
        session.add(provider)
        session.commit()

        response = client.delete("/api/admin/settings/accounts/oauth/google", headers=get_auth_headers(session))
        assert response.status_code == 400
        assert "only login method" in response.json()["detail"]

    def test_disconnect_with_real_password_allowed(self, client: TestClient, session: Session):
        """Should allow disconnect if user has a real password."""
        admin = session.exec(select(User)).first()
        # Admin has a real password from seed
        provider = UserOAuthProvider(user_id=admin.id, provider="google", provider_user_id="g-123")
        session.add(provider)
        session.commit()

        response = client.delete("/api/admin/settings/accounts/oauth/google", headers=get_auth_headers(session))
        assert response.status_code == 200
