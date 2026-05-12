import secrets
from urllib.parse import urlencode
from authlib.integrations.starlette_client import OAuth
from app.config import settings

SUPPORTED_PROVIDERS = {"google", "github"}

PROVIDER_CONFIGS = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "scope": "openid email profile",
    },
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "scope": "user:email",
    },
}


class OAuthService:
    def __init__(self):
        self.oauth = OAuth()
        self._register_providers()

    def _register_providers(self):
        if settings.GOOGLE_CLIENT_ID:
            self.oauth.register(
                "google",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_kwargs={"scope": "openid email profile"},
            )
        if settings.GITHUB_CLIENT_ID:
            self.oauth.register(
                "github",
                client_id=settings.GITHUB_CLIENT_ID,
                client_secret=settings.GITHUB_CLIENT_SECRET,
                access_token_url="https://github.com/login/oauth/access_token",
                authorize_url="https://github.com/login/oauth/authorize",
                client_kwargs={"scope": "user:email"},
            )

    def get_authorization_url(self, provider: str, redirect_uri: str) -> tuple[str, str]:
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        config = PROVIDER_CONFIGS[provider]
        client = self.oauth.create_client(provider)
        if client is None:
            raise ValueError(f"Provider {provider} is not configured")

        state = secrets.token_urlsafe(32)
        params = {
            "response_type": "code",
            "client_id": client.client_id,
            "redirect_uri": redirect_uri,
            "scope": config["scope"],
            "state": state,
        }
        url = f"{config['authorize_url']}?{urlencode(params)}"
        return url, state

    def handle_callback(self, provider: str, code: str, state: str) -> dict:
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        user_info = self._exchange_code(provider, code, state)
        return self.extract_user_info(provider, user_info)

    def _exchange_code(self, provider: str, code: str, state: str) -> dict:
        """Exchange authorization code for user info. Implemented by subclasses or mocked in tests."""
        raise NotImplementedError("Use the router endpoint for real OAuth flow")

    def extract_user_info(self, provider: str, user_info: dict) -> dict:
        if provider == "google":
            return {
                "email": user_info.get("email"),
                "provider_user_id": user_info.get("sub"),
                "email_verified": user_info.get("email_verified", False),
                "name": user_info.get("name", ""),
            }
        elif provider == "github":
            return {
                "email": user_info.get("email"),
                "provider_user_id": str(user_info.get("id", "")),
                "email_verified": user_info.get("email_verified", False),
                "name": user_info.get("name", "") or user_info.get("login", ""),
            }
        else:
            raise ValueError(f"Unsupported provider: {provider}")
