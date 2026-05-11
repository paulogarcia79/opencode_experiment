# QA Checklist: API Rate Limiting

## 1. Prerequisites & Setup

- [ ] Backend dev server running (`just back` or `uvicorn app.main:app --reload`)
- [ ] Redis running (default `redis://localhost:6379/0`)
- [ ] At least one published article exists in the database (for article view and search tests)
- [ ] No custom rate limit env vars set (use defaults for this QA pass)

---

## 2. Backend API Checks

### Search Endpoint (`GET /api/articles/search`)

- [ ] **Action:** Send 10 rapid `GET /api/articles/search?q=test` requests → **Expected:** All return `200` with article results
- [ ] **Action:** Send 11th request immediately after → **Expected:** `429` with body `{"detail": "Rate limit exceeded. Try again in X seconds."}` and `Retry-After` header > 0

### Subscribe Endpoint (`POST /api/subscribers`)

- [ ] **Action:** Send 3 rapid `POST /api/subscribers` with different emails → **Expected:** All return `200` with confirmation message
- [ ] **Action:** Send 4th request immediately after → **Expected:** `429` with `Retry-After` header and rate limit error body

### Article View Endpoint (`GET /api/articles/{slug}`)

- [ ] **Action:** Send 30 rapid `GET /api/articles/{existing-slug}` requests → **Expected:** All return `200` with article data
- [ ] **Action:** Send 31st request immediately after → **Expected:** `429` with `Retry-After` header and rate limit error body

### Unchanged Endpoints (should NOT be rate-limited)

- [ ] **Action:** Send 50+ rapid `GET /api/articles` requests → **Expected:** All return `200`
- [ ] **Action:** Send 50+ rapid `GET /feed.xml` requests → **Expected:** All return `200`
- [ ] **Action:** Send 50+ rapid `GET /sitemap.xml` requests → **Expected:** All return `200`
- [ ] **Action:** Send 50+ rapid `GET /robots.txt` requests → **Expected:** All return `200`

### Admin Endpoints (should bypass rate limiting)

- [ ] **Action:** Send 50+ rapid `GET /api/admin/articles` with valid admin JWT → **Expected:** All return `200` (never `429`)
- [ ] **Action:** Send 50+ rapid `POST /api/admin/articles` with valid admin JWT → **Expected:** All return `200` or `400` (validation errors, never `429`)

---

## 3. Frontend UI Checks

_No frontend changes were made. Rate limiting is purely backend. The frontend should gracefully handle `429` responses if they occur during normal use (unlikely with default limits)._

---

## 4. Edge Cases & Error Handling

- [ ] **Action:** Wait 60+ seconds after hitting rate limit, then retry → **Expected:** Request succeeds (window reset)
- [ ] **Action:** Send search request with empty `q` parameter → **Expected:** `400` (validation error, not rate limited)
- [ ] **Action:** Send subscribe request with invalid email format → **Expected:** `422` (validation error, not rate limited)
- [ ] **Action:** Send article view request for non-existent slug → **Expected:** `404` (not found, not rate limited)
- [ ] **Action:** Send admin request without auth token → **Expected:** `401` (unauthorized, not `429`)

---

## 5. Integration Checks

- [ ] **Action:** Hit search rate limit, wait for `Retry-After` seconds, retry → **Expected:** Request succeeds after window expires
- [ ] **Action:** Configure `RATE_LIMIT_SEARCH=2/minute` in `.env`, restart backend → **Expected:** Search endpoint now limits at 2 requests/minute (configurable)
- [ ] **Action:** Send requests with `X-Forwarded-For: 1.2.3.4` header (simulate Nginx proxy) → **Expected:** Rate limit tracks by forwarded IP, not local host
- [ ] **Action:** Restart backend while rate limit is active → **Expected:** Rate limit state persists (stored in Redis, not memory)
- [ ] **Action:** Verify `Retry-After` header value matches actual seconds until reset → **Expected:** Header value is accurate (within 1-second tolerance)
