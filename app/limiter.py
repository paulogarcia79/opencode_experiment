from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings


def get_limiter() -> Limiter:
    """Create and return a Limiter instance configured with Redis or memory fallback."""
    return Limiter(
        key_func=get_remote_address,
        storage_uri=settings.REDIS_URL,
        strategy="fixed-window",
    )


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    retry_after = exc.limit.limit.get_expiry()
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded. Try again in {retry_after} seconds."},
        headers={"Retry-After": str(retry_after)},
    )
