## Problem Statement

Public-facing API endpoints on the blog are completely unprotected from abuse. Anyone can hammer the search endpoint with thousands of requests per minute (expensive LIKE queries against the database), spam the subscription endpoint to flood the email list, or scrape all article content by rapidly fetching article slugs. As the blog grows in visibility, this becomes a real risk: database performance degrades under abusive load, Resend email quotas get exhausted by subscription spam, and competitors can scrape the entire content library in seconds. There is currently no mechanism to reject or throttle excessive requests.

## Solution

Add API rate limiting to the three most vulnerable public endpoints: article search, article views, and subscription. Each endpoint gets its own configurable rate limit enforced per client IP address. When a client exceeds the limit, they receive a `429 Too Many Requests` response with a `Retry-After` header and a structured JSON error body. The system uses `slowapi` with Redis as the backend (reusing the existing Redis instance already running for ARQ background jobs), so no new infrastructure is required.

## User Stories

1. As a reader, I want to search for articles without being blocked by rate limits during normal use, so that I can find content efficiently
2. As a reader, I want to read articles without interruption, so that my browsing experience is not degraded
3. As a reader, I want to subscribe to the newsletter without being blocked, so that I can receive updates
4. As a site owner, I want abusive traffic to be automatically throttled, so that my database and email service are protected from overload
5. As a site owner, I want rate limits to be configurable via environment variables, so that I can adjust them based on real traffic patterns without code changes
6. As a site owner, I want rate-limited clients to receive a clear `429` response with a retry-after time, so that legitimate users know when they can try again
7. As a developer, I want rate limiting to use the existing Redis instance, so that no additional infrastructure is required
8. As a developer, I want rate limits to be applied via decorators on specific endpoints, so that the implementation is declarative and easy to understand
9. As a developer, I want authenticated admin requests to bypass rate limits, so that administrative workflows are never blocked
10. As a developer, I want the rate limit middleware to correctly identify client IP behind Nginx (via `X-Forwarded-For`), so that production traffic is rate-limited accurately
11. As a developer, I want rate limit state to persist across server restarts (via Redis), so that abusers cannot bypass limits by restarting the app
12. As a developer, I want the rate limiting module to be testable in isolation, so that I can verify behavior without hitting Redis in unit tests

## Implementation Decisions

### Modules

**Slowapi Integration (Middleware)**
- Add `slowapi` to `pyproject.toml` dependencies
- Register `SlowAPI` extension in `app/main.py` as middleware, configured with Redis backend
- Redis connection reuses the existing `REDIS_URL` from `settings` — no new env var needed
- Configure a custom rate limit exceeded handler that returns `429` with JSON body: `{"detail": "Rate limit exceeded. Try again in X seconds."}`

**Rate Limit Configuration**
- New settings in `app/config.py`:
  - `RATE_LIMIT_SEARCH: str = "10/minute"`
  - `RATE_LIMIT_SUBSCRIBE: str = "3/minute"`
  - `RATE_LIMIT_ARTICLE_VIEW: str = "30/minute"`
- All configurable via `.env` with sensible defaults hardcoded

**Endpoint Decorators**
- Apply `@limiter.limit(settings.RATE_LIMIT_SEARCH)` to `GET /api/articles/search`
- Apply `@limiter.limit(settings.RATE_LIMIT_SUBSCRIBE)` to `POST /api/subscribers`
- Apply `@limiter.limit(settings.RATE_LIMIT_ARTICLE_VIEW)` to `GET /api/articles/{slug}`
- Admin endpoints (protected by `require_admin`) are NOT rate-limited — JWT auth is sufficient protection

**IP Extraction**
- Nginx already sets `X-Forwarded-For` and `X-Real-IP` headers (confirmed in `nginx.dev.conf`)
- `slowapi` supports reading from `X-Forwarded-For` out of the box — configure it to trust proxy headers
- Falls back to `request.client.host` when no proxy headers present (dev mode without Nginx)

### API Contract

**Rate-Limited Responses**
- `429 Too Many Requests`
  - Header: `Retry-After: <seconds until reset>`
  - Body: `{"detail": "Rate limit exceeded. Try again in X seconds."}`
- All other responses unchanged

**Unchanged Endpoints**
- `GET /api/articles` (list) — not rate-limited (cheap query, low abuse risk)
- `GET /feed.xml`, `GET /sitemap.xml`, `GET /robots.txt` — not rate-limited (RSS crawlers and search engines need unrestricted access)
- `GET /api/tags/{slug}` — not rate-limited in this iteration (can be added later if needed)

### Configuration

```env
RATE_LIMIT_SEARCH=10/minute
RATE_LIMIT_SUBSCRIBE=3/minute
RATE_LIMIT_ARTICLE_VIEW=30/minute
```

Format follows slowapi's standard: `<count>/<period>` where period is `second`, `minute`, `hour`, or `day`.

### Schema Changes

None. Rate limiting is stateless at the database level — all state lives in Redis.

## Testing Decisions

**What makes a good test:** Test behavior through public interfaces. Verify that requests within the limit succeed (200), requests exceeding the limit are rejected (429), and the `Retry-After` header is present. Do not test slowapi internals or Redis key construction.

**Modules to test:**
- Rate limit middleware: verify 429 response when limit is exceeded, verify Retry-After header, verify JSON error body
- Search endpoint: verify first 10 requests succeed, 11th is rejected
- Subscribe endpoint: verify first 3 requests succeed, 4th is rejected
- Article view endpoint: verify first 30 requests succeed, 31st is rejected
- Admin endpoints: verify they are NOT rate-limited (authenticated requests bypass)
- IP extraction: verify X-Forwarded-For header is respected

**Prior art:**
- Backend tests use `TestClient` + `session` fixtures (see `test_articles.py` for endpoint testing patterns)
- The existing `test_auth.py` already has a rate-limiting test for forgot-password cooldown (see `test_forgot_password_cooldown`) — follow similar pattern of rapid sequential requests
- Tests use SQLite in-memory via `tests/conftest.py` — Redis will need to be mocked or a test Redis instance used

**Testing approach:**
- Mock the Redis backend in tests using slowapi's `MemoryStorage` instead of Redis, so tests don't require a running Redis instance
- Use the `limiter.reset()` method between tests to clear state
- Each test file should be independent and not share rate limit state

## Out of Scope

- Rate limiting for `GET /api/articles` (list endpoint) — deferred; low cost query, can be added if abuse is observed
- Rate limiting for `GET /api/tags/{slug}` — deferred; can be added in a future iteration
- Rate limiting for `GET /feed.xml`, `GET /sitemap.xml`, `GET /robots.txt` — intentionally excluded; RSS crawlers and search engine bots need unrestricted access
- Per-user rate limiting — not applicable since public endpoints are unauthenticated
- Rate limiting dashboard or admin UI — purely operational, no visibility needed at this scale
- Custom rate limit response format beyond standard 429 — no need to reinvent
- Rate limiting for admin endpoints — JWT authentication is sufficient protection
- DDoS protection at the network layer — this is application-level rate limiting only; infrastructure-level DDoS protection (Cloudflare, etc.) is a separate concern
- Sliding window rate limiting — slowapi uses fixed window by default; sufficient for this use case

## Further Notes

- `slowapi` version should be pinned in `pyproject.toml` to avoid breaking changes
- The existing password reset cooldown in `app/routers/auth.py` uses an in-memory approach — this could be migrated to use slowapi in a future cleanup, but is out of scope for this change
- Redis is already a required dependency for ARQ background jobs, so this adds zero new infrastructure
- In production, ensure Nginx is configured to pass `X-Forwarded-For` (already confirmed in `nginx.dev.conf` and `nginx.prod.conf`)
- Consider adding rate limit headers to successful responses (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) as a future enhancement for transparency
