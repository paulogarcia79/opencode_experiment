## What to build

Add `slowapi` dependency and register it as middleware in the FastAPI app with Redis backend. Configure a custom rate limit exceeded handler that returns `429` with a structured JSON body. Add rate limit configuration settings to `app/config.py` with env var support. This is the foundation that all subsequent rate-limited endpoints depend on.

## Acceptance criteria

- [x] `slowapi` added to `pyproject.toml` and installed
- [x] `SlowAPI` registered as middleware in `app/main.py` with Redis backend (reusing existing `REDIS_URL`)
- [x] Custom rate limit exceeded handler returns `429` with JSON body: `{"detail": "Rate limit exceeded. Try again in X seconds."}` and `Retry-After` header
- [x] New settings in `app/config.py`: `RATE_LIMIT_SEARCH`, `RATE_LIMIT_SUBSCRIBE`, `RATE_LIMIT_ARTICLE_VIEW` with defaults `"10/minute"`, `"3/minute"`, `"30/minute"`
- [x] Settings are configurable via `.env` file
- [x] Tests verify 429 response format when limit is exceeded (using `MemoryStorage` instead of Redis)
- [x] Existing tests continue to pass (no regression from middleware addition)

## Blocked by

None - can start immediately

## Implementation Notes

- Created `app/limiter.py` with `get_limiter()` and `rate_limit_exceeded_handler()`
- Registered `SlowAPIMiddleware` in `app/main.py`
- All 166 tests pass (162 existing + 4 new)
- Decorator order matters: `@app.get()` must come before `@limiter.limit()`
