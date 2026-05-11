## Parent

PRD: API Rate Limiting

## What to build

Apply rate limiting to the article search endpoint (`GET /api/articles/search`). This is the most expensive public endpoint (LIKE queries + ranking) and the highest abuse risk. Decorate the endpoint with `@limiter.limit(settings.RATE_LIMIT_SEARCH)` and verify the limit is enforced via tests.

## Acceptance criteria

- [x] `GET /api/articles/search` decorated with `@limiter.limit(settings.RATE_LIMIT_SEARCH)`
- [x] First 10 requests within a minute succeed with `200`
- [x] 11th request within the same minute returns `429` with `Retry-After` header
- [x] `Retry-After` header value is correct (seconds until window reset)
- [x] Test uses `MemoryStorage` (no Redis dependency)
- [x] Existing search functionality unchanged (results still returned correctly)

## Blocked by

- #1 Rate Limit Infrastructure

## Implementation Notes

- Refactored limiter.py to export shared limiter instance (singleton pattern)
- Added limiter.reset() to conftest.py to prevent test pollution
- Added TestSearchRateLimit class with 2 tests
- All 168 tests pass
