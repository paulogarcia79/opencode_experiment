## Parent

PRD: API Rate Limiting

## What to build

Verify that authenticated admin endpoints bypass rate limiting and that IP extraction works correctly behind Nginx (via `X-Forwarded-For` header). Add tests to ensure admin workflows are never blocked and production traffic is rate-limited accurately.

## Acceptance criteria

- [x] Admin endpoints (protected by `require_admin`) are NOT rate-limited — rapid requests succeed
- [x] `X-Forwarded-For` header is respected for IP identification in rate limiting
- [x] Falls back to `request.client.host` when no proxy headers present
- [x] Tests verify admin bypass behavior
- [x] Tests verify different IPs have separate rate limits
- [x] All existing tests continue to pass

## Blocked by

- #2 Rate Limit Search
- #3 Rate Limit Subscribe
- #4 Rate Limit Article View
