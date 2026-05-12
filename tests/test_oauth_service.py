import pytest
from unittest.mock import patch, MagicMock
from app.services.oauth_service import OAuthService
from app.config import settings


@pytest.fixture(autouse=True)
def configure_oauth_credentials():
    """Ensure OAuth credentials are set for tests."""
    original_google_id = settings.GOOGLE_CLIENT_ID
    original_google_secret = settings.GOOGLE_CLIENT_SECRET
    original_github_id = settings.GITHUB_CLIENT_ID
    original_github_secret = settings.GITHUB_CLIENT_SECRET

    settings.GOOGLE_CLIENT_ID = "test-google-id"
    settings.GOOGLE_CLIENT_SECRET = "test-google-secret"
    settings.GITHUB_CLIENT_ID = "test-github-id"
    settings.GITHUB_CLIENT_SECRET = "test-github-secret"

    yield

    settings.GOOGLE_CLIENT_ID = original_google_id
    settings.GOOGLE_CLIENT_SECRET = original_google_secret
    settings.GITHUB_CLIENT_ID = original_github_id
    settings.GITHUB_CLIENT_SECRET = original_github_secret


class TestOAuthServiceAuthorizationURL:
    """Test authorization URL generation."""

    def test_google_authorization_url_contains_google_endpoint(self, configure_oauth_credentials):
        """Google auth URL should point to Google's authorization endpoint."""
        service = OAuthService()
        url, state = service.get_authorization_url("google", "http://localhost/callback")
        assert "accounts.google.com" in url
        assert "openid" in url
        assert state is not None
        assert len(state) > 10

    def test_google_authorization_url_contains_state(self, configure_oauth_credentials):
        """Authorization URL should include state parameter for CSRF protection."""
        service = OAuthService()
        url, state = service.get_authorization_url("google", "http://localhost/callback")
        assert f"state={state}" in url

    def test_unsupported_provider_raises_error(self):
        """Unsupported provider should raise ValueError."""
        service = OAuthService()
        with pytest.raises(ValueError, match="Unsupported provider"):
            service.get_authorization_url("twitter", "http://localhost/callback")


class TestOAuthServiceUserInfo:
    """Test user info extraction from OAuth providers."""

    def test_google_user_info_extracts_email(self):
        """Google user info should extract email."""
        service = OAuthService()
        user_info = {
            "sub": "google-12345",
            "email": "test@gmail.com",
            "email_verified": True,
            "name": "Test User",
        }
        result = service.extract_user_info("google", user_info)
        assert result["email"] == "test@gmail.com"
        assert result["provider_user_id"] == "google-12345"
        assert result["email_verified"] is True

    def test_google_user_info_extracts_provider_user_id(self):
        """Google user info should use 'sub' as provider_user_id."""
        service = OAuthService()
        user_info = {"sub": "unique-google-id", "email": "test@gmail.com", "email_verified": True}
        result = service.extract_user_info("google", user_info)
        assert result["provider_user_id"] == "unique-google-id"

    def test_google_user_info_email_not_verified(self):
        """Google user info should capture email_verified=False."""
        service = OAuthService()
        user_info = {"sub": "google-123", "email": "test@gmail.com", "email_verified": False}
        result = service.extract_user_info("google", user_info)
        assert result["email_verified"] is False

    def test_unsupported_provider_user_info_raises_error(self):
        """Unsupported provider should raise ValueError."""
        service = OAuthService()
        with pytest.raises(ValueError, match="Unsupported provider"):
            service.extract_user_info("twitter", {})


class TestOAuthServiceHandleCallback:
    """Test OAuth callback handling."""

    @patch("app.services.oauth_service.OAuthService._exchange_code")
    def test_google_callback_returns_user_info(self, mock_exchange, configure_oauth_credentials):
        """Google callback should return extracted user info."""
        mock_exchange.return_value = {
            "sub": "google-12345",
            "email": "test@gmail.com",
            "email_verified": True,
        }
        service = OAuthService()
        result = service.handle_callback("google", "auth-code", "state-value")
        assert result["email"] == "test@gmail.com"
        assert result["provider_user_id"] == "google-12345"
        assert result["email_verified"] is True


class TestOAuthServiceGitHub:
    """Test GitHub provider support."""

    def test_github_authorization_url(self, configure_oauth_credentials):
        """GitHub auth URL should point to GitHub's authorization endpoint."""
        service = OAuthService()
        url, state = service.get_authorization_url("github", "http://localhost/callback")
        assert "github.com/login/oauth/authorize" in url
        assert "user%3Aemail" in url or "user:email" in url
        assert state is not None

    def test_github_user_info_extracts_email(self):
        """GitHub user info should extract email."""
        service = OAuthService()
        user_info = {
            "id": 12345,
            "email": "test@github.com",
            "login": "testuser",
            "name": "Test User",
        }
        result = service.extract_user_info("github", user_info)
        assert result["email"] == "test@github.com"
        assert result["provider_user_id"] == "12345"
        assert result["name"] == "Test User"

    def test_github_user_info_uses_login_if_no_name(self):
        """GitHub user info should fall back to login if name is empty."""
        service = OAuthService()
        user_info = {"id": 999, "email": "test@github.com", "login": "nousername", "name": None}
        result = service.extract_user_info("github", user_info)
        assert result["name"] == "nousername"
