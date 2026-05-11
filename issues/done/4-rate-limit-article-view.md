## Parent

PRD: API Rate Limiting

## What to build

Apply rate limiting to the article view endpoint (`GET /api/articles/{slug}`). This prevents content scraping and excessive database load. Decorate the endpoint with `@limiter.limit(settings.RATE_LIMIT_ARTICLE_VIEW)` and verify the limit is enforced via tests.

## Acceptance criteria

- [x] `GET /api/articles/{slug}` decorated with `@limiter.limit(settings.RATE_LIMIT_ARTICLE_VIEW)`
- [x] First 30 requests within a minute succeed with `200`
- [x] 31st request within the same minute returns `429` with `Retry-After` header
- [x] Test uses `MemoryStorage` (no Redis dependency)
- [x] Existing article view functionality unchanged (view tracking still works)

## Blocked by

- #1 Rate Limit Infrastructure
