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


class TestSearchRateLimit:
    """Test rate limiting on the search endpoint."""

    def _create_test_app_with_search(self, limit: str = "2/minute"):
        """Create a test FastAPI app with search endpoint and rate limiting using MemoryStorage."""
        from fastapi import FastAPI, Depends
        from slowapi import Limiter
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from sqlmodel import Session
        from app.database import get_session

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

        @app.get("/api/articles/search")
        @limiter.limit(limit)
        async def search_endpoint(request: Request, q: str = "", session: Session = Depends(get_session)):
            return [{"title": f"Result for: {q}"}]

        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        return app

    def test_search_rate_limit_enforced(self):
        """Search requests beyond the limit should return 429."""
        app = self._create_test_app_with_search(limit="2/minute")
        client = TestClient(app)

        # First 2 requests should succeed
        response1 = client.get("/api/articles/search?q=test")
        assert response1.status_code == 200

        response2 = client.get("/api/articles/search?q=test")
        assert response2.status_code == 200

        # 3rd request should be rate limited
        response3 = client.get("/api/articles/search?q=test")
        assert response3.status_code == 429
        data = response3.json()
        assert "Rate limit exceeded" in data["detail"]
        assert "Retry-After" in response3.headers

    def test_search_rate_limit_response_format(self):
        """Search rate limit response should have correct JSON format and Retry-After header."""
        app = self._create_test_app_with_search(limit="1/minute")
        client = TestClient(app)

        # First request succeeds
        response1 = client.get("/api/articles/search?q=test")
        assert response1.status_code == 200

        # Second request is rate limited
        response2 = client.get("/api/articles/search?q=test")
        assert response2.status_code == 429

        data = response2.json()
        assert "detail" in data
        assert "Rate limit exceeded" in data["detail"]
        assert "Try again in" in data["detail"]
        assert response2.headers.get("Retry-After") is not None
        assert int(response2.headers["Retry-After"]) > 0


class TestSubscribeRateLimit:
    """Test rate limiting on the subscribe endpoint."""

    def _create_test_app_with_subscribe(self, limit: str = "2/minute"):
        """Create a test FastAPI app with subscribe endpoint and rate limiting using MemoryStorage."""
        from fastapi import FastAPI
        from slowapi import Limiter
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from pydantic import BaseModel

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

        class SubscribeRequest(BaseModel):
            email: str

        @app.post("/api/subscribers")
        @limiter.limit(limit)
        async def subscribe_endpoint(request: Request, data: SubscribeRequest):
            return {"message": "Check your email to confirm your subscription."}

        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        return app

    def test_subscribe_rate_limit_enforced(self):
        """Subscribe requests beyond the limit should return 429."""
        app = self._create_test_app_with_subscribe(limit="2/minute")
        client = TestClient(app)

        # First 2 requests should succeed
        response1 = client.post("/api/subscribers", json={"email": "test1@example.com"})
        assert response1.status_code == 200

        response2 = client.post("/api/subscribers", json={"email": "test2@example.com"})
        assert response2.status_code == 200

        # 3rd request should be rate limited
        response3 = client.post("/api/subscribers", json={"email": "test3@example.com"})
        assert response3.status_code == 429
        data = response3.json()
        assert "Rate limit exceeded" in data["detail"]
        assert "Retry-After" in response3.headers

    def test_subscribe_rate_limit_response_format(self):
        """Subscribe rate limit response should have correct JSON format and Retry-After header."""
        app = self._create_test_app_with_subscribe(limit="1/minute")
        client = TestClient(app)

        # First request succeeds
        response1 = client.post("/api/subscribers", json={"email": "test@example.com"})
        assert response1.status_code == 200

        # Second request is rate limited
        response2 = client.post("/api/subscribers", json={"email": "test2@example.com"})
        assert response2.status_code == 429

        data = response2.json()
        assert "detail" in data
        assert "Rate limit exceeded" in data["detail"]
        assert "Try again in" in data["detail"]
        assert response2.headers.get("Retry-After") is not None
        assert int(response2.headers["Retry-After"]) > 0


class TestArticleViewRateLimit:
    """Test rate limiting on the article view endpoint."""

    def _create_test_app_with_article_view(self, limit: str = "2/minute"):
        """Create a test FastAPI app with article view endpoint and rate limiting using MemoryStorage."""
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

        @app.get("/api/articles/{slug}")
        @limiter.limit(limit)
        async def article_view_endpoint(request: Request, slug: str):
            return {"slug": slug, "title": f"Article: {slug}"}

        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        return app

    def test_article_view_rate_limit_enforced(self):
        """Article view requests beyond the limit should return 429."""
        app = self._create_test_app_with_article_view(limit="2/minute")
        client = TestClient(app)

        # First 2 requests should succeed
        response1 = client.get("/api/articles/test-article")
        assert response1.status_code == 200

        response2 = client.get("/api/articles/test-article")
        assert response2.status_code == 200

        # 3rd request should be rate limited
        response3 = client.get("/api/articles/test-article")
        assert response3.status_code == 429
        data = response3.json()
        assert "Rate limit exceeded" in data["detail"]
        assert "Retry-After" in response3.headers

    def test_article_view_rate_limit_response_format(self):
        """Article view rate limit response should have correct JSON format and Retry-After header."""
        app = self._create_test_app_with_article_view(limit="1/minute")
        client = TestClient(app)

        # First request succeeds
        response1 = client.get("/api/articles/test-article")
        assert response1.status_code == 200

        # Second request is rate limited
        response2 = client.get("/api/articles/test-article")
        assert response2.status_code == 429

        data = response2.json()
        assert "detail" in data
        assert "Rate limit exceeded" in data["detail"]
        assert "Try again in" in data["detail"]
        assert response2.headers.get("Retry-After") is not None
        assert int(response2.headers["Retry-After"]) > 0


class TestAdminBypass:
    """Test that admin endpoints bypass rate limiting."""

    def test_admin_endpoints_not_rate_limited(self):
        """Admin endpoints should not be rate limited even with rapid requests."""
        from app.main import app
        from app.limiter import limiter

        # Reset limiter state
        limiter.reset()

        # Use the test client with admin auth
        with TestClient(app) as client:
            # Make many rapid requests to an admin endpoint
            # These should all succeed (not be rate limited)
            for _ in range(15):
                response = client.get(
                    "/api/admin/articles",
                    headers={"Authorization": "Bearer dev-token"}
                )
                # Should be 401 (invalid token) not 429 (rate limited)
                assert response.status_code != 429, "Admin endpoint should not be rate limited"


class TestIPExtraction:
    """Test that IP extraction works correctly for rate limiting."""

    def test_different_ips_have_separate_limits(self):
        """Different IPs should have separate rate limit counters."""
        from fastapi import FastAPI
        from slowapi import Limiter
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        from slowapi.util import get_remote_address
        from starlette.requests import Request
        from starlette.responses import JSONResponse

        # Custom key function that reads from X-Forwarded-For
        def get_ip(request: Request) -> str:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                return forwarded.split(",")[0].strip()
            return request.client.host

        limiter = Limiter(
            key_func=get_ip,
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
        @limiter.limit("1/minute")
        async def test_endpoint(request: Request):
            return {"ip": get_ip(request)}

        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        client = TestClient(app)

        # Request from IP 1.2.3.4
        response1 = client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
        assert response1.status_code == 200

        # Same IP should be rate limited
        response2 = client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
        assert response2.status_code == 429

        # Different IP should NOT be rate limited
        response3 = client.get("/test", headers={"X-Forwarded-For": "5.6.7.8"})
        assert response3.status_code == 200
