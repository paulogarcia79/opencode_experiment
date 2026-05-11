## Parent

PRD: API Rate Limiting

## What to build

Apply rate limiting to the subscription endpoint (`POST /api/subscribers`). This prevents email list spam and Resend quota exhaustion. Decorate the endpoint with `@limiter.limit(settings.RATE_LIMIT_SUBSCRIBE)` and verify the limit is enforced via tests.

## Acceptance criteria

- [x] `POST /api/subscribers` decorated with `@limiter.limit(settings.RATE_LIMIT_SUBSCRIBE)`
- [x] First 3 requests within a minute succeed with `200`
- [x] 4th request within the same minute returns `429` with `Retry-After` header
- [x] Test uses `MemoryStorage` (no Redis dependency)
- [x] Existing subscription functionality unchanged (confirmation emails still sent)

## Blocked by

- #1 Rate Limit Infrastructure
