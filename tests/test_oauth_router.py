import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.config import settings
from app.models.user import User
from app.models.user_oauth_provider import UserOAuthProvider


@pytest.fixture(autouse=True)
def configure_oauth_credentials():
    original_google_id = settings.GOOGLE_CLIENT_ID
    original_google_secret = settings.GOOGLE_CLIENT_SECRET
    settings.GOOGLE_CLIENT_ID = "test-google-id"
    settings.GOOGLE_CLIENT_SECRET = "test-google-secret"
    yield
    settings.GOOGLE_CLIENT_ID = original_google_id
    settings.GOOGLE_CLIENT_SECRET = original_google_secret


class TestOAuthInitiate:
    """Test OAuth initiation endpoint."""

    def test_google_oauth_redirect(self, client: TestClient):
        """GET /api/auth/oauth/google should redirect to Google."""
        response = client.get("/api/auth/oauth/google", follow_redirects=False)
        assert response.status_code == 307
        assert "accounts.google.com" in response.headers["location"]
        assert "state=" in response.headers["location"]

    def test_unsupported_provider_404(self, client: TestClient):
        """GET /api/auth/oauth/twitter should return 404."""
        response = client.get("/api/auth/oauth/twitter")
        assert response.status_code == 404


class TestOAuthCallback:
    """Test OAuth callback endpoint."""

    def _mock_google_token_response(self, monkeypatch):
        """Mock the token exchange to return user info directly."""
        from app.routers import oauth as oauth_router

        async def mock_authorize_redirect(self, request, redirect_uri):
            from starlette.responses import RedirectResponse
            return RedirectResponse(url=redirect_uri + "?code=fake-code&state=test-state")

        async def mock_parse_authorization_response(self, request, redirect_uri):
            return {"code": "fake-code", "state": "test-state"}

        async def mock_fetch_token(self, code, redirect_uri):
            return {"access_token": "fake-token"}

        async def mock_userinfo(self, token=None):
            return {
                "sub": "google-12345",
                "email": "oauth-user@gmail.com",
                "email_verified": True,
                "name": "OAuth User",
            }

        monkeypatch.setattr(
            "app.routers.oauth.OAuthHandler._authorize_redirect",
            lambda self, request, redirect_uri: mock_authorize_redirect(self, request, redirect_uri),
        )
        monkeypatch.setattr(
            "app.routers.oauth.OAuthHandler._parse_callback",
            lambda self, request: {"code": "fake-code", "state": "test-state"},
        )
        monkeypatch.setattr(
            "app.routers.oauth.OAuthHandler._exchange_code",
            lambda self, code, redirect_uri: {"access_token": "fake-token"},
        )
        monkeypatch.setattr(
            "app.routers.oauth.OAuthHandler._fetch_userinfo",
            lambda self, token: {
                "sub": "google-12345",
                "email": "oauth-user@gmail.com",
                "email_verified": True,
                "name": "OAuth User",
            },
        )

    def test_callback_creates_new_user(self, client: TestClient, session: Session, monkeypatch):
        """OAuth callback for new user should create account and redirect to verify-email."""
        from unittest.mock import patch, AsyncMock
        from app.routers import oauth as oauth_router

        # Populate state store (normally done by initiate step)
        oauth_router._oauth_states["test-state"] = "http://test/api/auth/oauth/google/callback"

        initial_count = session.exec(select(User)).all().__len__()

        with patch.object(oauth_router.OAuthHandler, "_exchange_code", return_value={"access_token": "fake-token"}):
            with patch.object(oauth_router.OAuthHandler, "_fetch_userinfo", return_value={
                "sub": "google-12345",
                "email": "new-oauth-user@gmail.com",
                "email_verified": True,
                "name": "New User",
            }):
                response = client.get(
                    "/api/auth/oauth/google/callback",
                    params={"code": "fake-code", "state": "test-state"},
                    follow_redirects=False,
                )
                # Should redirect to verify-email page
                assert response.status_code == 302
                assert "/admin/verify-email" in response.headers["location"]

    def test_callback_links_existing_user(self, client: TestClient, session: Session, monkeypatch):
        """OAuth callback for existing email should link accounts and redirect with JWT."""
        from unittest.mock import patch
        from app.routers import oauth as oauth_router

        # Populate state store
        oauth_router._oauth_states["test-state"] = "http://test/api/auth/oauth/google/callback"

        # Admin user already exists from fixture
        admin = session.exec(select(User)).first()

        with patch.object(oauth_router.OAuthHandler, "_exchange_code", return_value={"access_token": "fake-token"}):
            with patch.object(oauth_router.OAuthHandler, "_fetch_userinfo", return_value={
                "sub": "google-99999",
                "email": admin.email,
                "email_verified": True,
                "name": "Admin User",
            }):
                response = client.get(
                    "/api/auth/oauth/google/callback",
                    params={"code": "fake-code", "state": "test-state"},
                    follow_redirects=False,
                )
                # Should redirect to /admin/login with oauth_token
                assert response.status_code == 302
                assert "/admin/login?oauth_token=" in response.headers["location"]

                # Verify OAuth provider was linked
                providers = session.exec(
                    select(UserOAuthProvider).where(
                        UserOAuthProvider.user_id == admin.id,
                        UserOAuthProvider.provider == "google",
                    )
                ).all()
                assert len(providers) == 1
                assert providers[0].provider_user_id == "google-99999"

    def test_github_callback_creates_new_user(self, client: TestClient, session: Session):
        """GitHub OAuth callback for new user should create account and redirect to verify-email."""
        from unittest.mock import patch
        from app.routers import oauth as oauth_router

        oauth_router._oauth_states["test-state"] = "http://test/api/auth/oauth/github/callback"

        with patch.object(oauth_router.OAuthHandler, "_exchange_code", return_value={"access_token": "fake-token"}):
            with patch.object(oauth_router.OAuthHandler, "_fetch_userinfo", return_value={
                "id": 54321,
                "email": "github-user@github.com",
                "login": "githubuser",
                "name": "GitHub User",
            }):
                response = client.get(
                    "/api/auth/oauth/github/callback",
                    params={"code": "fake-code", "state": "test-state"},
                    follow_redirects=False,
                )
                assert response.status_code == 302
                assert "/admin/verify-email" in response.headers["location"]

                # Verify user was created with GitHub provider
                new_user = session.exec(select(User).where(User.email == "github-user@github.com")).first()
                assert new_user is not None
                assert new_user.is_verified is False

                providers = session.exec(
                    select(UserOAuthProvider).where(
                        UserOAuthProvider.user_id == new_user.id,
                        UserOAuthProvider.provider == "github",
                    )
                ).all()
                assert len(providers) == 1
                assert providers[0].provider_user_id == "54321"
