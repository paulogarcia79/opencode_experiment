import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from slowapi import Limiter
from slowapi.util import get_remote_address
from limits import parse


class TestRateLimitConfig:
    """Test rate limit configuration settings."""

    def test_rate_limit_settings_exist(self):
        """Rate limit settings should exist with default values."""
        from app.config import settings
        assert hasattr(settings, 'RATE_LIMIT_SEARCH')
        assert hasattr(settings, 'RATE_LIMIT_SUBSCRIBE')
        assert hasattr(settings, 'RATE_LIMIT_ARTICLE_VIEW')

    def test_rate_limit_defaults(self):
        """Rate limit settings should have correct default values."""
        from app.config import settings
        assert settings.RATE_LIMIT_SEARCH == "10/minute"
        assert settings.RATE_LIMIT_SUBSCRIBE == "3/minute"
        assert settings.RATE_LIMIT_ARTICLE_VIEW == "30/minute"


class TestRateLimitMiddleware:
    """Test rate limiting middleware behavior."""

    def _create_test_app(self, limit: str = "2/minute"):
        """Create a test FastAPI app with rate limiting using MemoryStorage."""
        from fastapi import FastAPI
        from slowapi import Limiter
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        from starlette.requests import Request
        from starlette.responses import JSONResponse

        limiter = Limiter(
            key_func=lambda: "test_client",
            storage_uri="memory://",
        )

        app = FastAPI()

        @app.exception_handler(RateLimitExceeded)
        async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
            retry_after = exc.limit.limit.get_expiry()
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded. Try again in {retry_after} seconds."},
                headers={"Retry-After": str(retry_after)},
            )

        @app.get("/test")
        @limiter.limit(limit)
        async def test_endpoint(request: Request):
            return {"message": "ok"}

        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        return app

    def test_rate_limit_enforced(self):
        """Requests beyond the limit should return 429."""
        app = self._create_test_app(limit="2/minute")
        client = TestClient(app)

        # First 2 requests should succeed
        response1 = client.get("/test")
        assert response1.status_code == 200

        response2 = client.get("/test")
        assert response2.status_code == 200

        # 3rd request should be rate limited
        response3 = client.get("/test")
        assert response3.status_code == 429
        data = response3.json()
        assert "Rate limit exceeded" in data["detail"]
        assert "Retry-After" in response3.headers

    def test_rate_limit_response_format(self):
        """Rate limit response should have correct JSON format and Retry-After header."""
        app = self._create_test_app(limit="1/minute")
        client = TestClient(app)

        # First request succeeds
        response1 = client.get("/test")
        assert response1.status_code == 200

        # Second request is rate limited
        response2 = client.get("/test")
        assert response2.status_code == 429

        data = response2.json()
        assert "detail" in data
        assert "Rate limit exceeded" in data["detail"]
        assert "Try again in" in data["detail"]
        assert response2.headers.get("Retry-After") is not None
        assert int(response2.headers["Retry-After"]) > 0
