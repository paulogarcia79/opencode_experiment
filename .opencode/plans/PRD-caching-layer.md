## Problem Statement

The public endpoints for the blog application (`/api/articles`, `/api/articles/{slug}`, and `/feed.xml`) currently query the database directly on every request. This could lead to a bottleneck and slow response times if the blog experiences a spike in traffic, potentially degrading the user experience and increasing infrastructure costs.

## Solution

Implement a Redis caching layer using `fastapi-cache2` to cache the responses of the high-traffic public endpoints. This will significantly reduce database load and improve response times for end users. The cache will be invalidated dynamically (event-driven) whenever articles are created, updated, or deleted, ensuring users always see the latest content without unnecessary delays. To support caching the article detail endpoint while still tracking views, view tracking will be moved to a separate client-side API call.

## User Stories

1. As a reader, I want the homepage article list to load instantly, so that I can quickly browse content.
2. As a reader, I want individual articles to load instantly, so that I don't experience lag when clicking a link.
3. As a blog admin, I want my RSS subscribers' feed readers to fetch updates quickly without overwhelming my database, so that my infrastructure scales efficiently.
4. As a blog admin, I want article views to be accurately tracked even when the article content is served from the cache, so that my analytics remain reliable.
5. As an editor, I want any changes I make to a published article to be immediately visible to the public, so that I don't have to wait for a time-to-live (TTL) to expire.
6. As an editor, I want to be able to preview unpublished drafts, so that I can review them before they go live.
7. As an admin, I want my admin API endpoints to never be cached, so that I always see real-time data when managing the platform.

## Implementation Decisions

- **Library:** Use `fastapi-cache2` with the `redis.asyncio` backend for caching implementation.
- **Initialization:** Initialize `FastAPICache` within the application's lifespan block (`app/main.py`), reusing or aligning with the existing Redis connection configurations (`app.redis.get_redis_settings()`).
- **Endpoints to Cache:**
  - `GET /api/articles` (List published articles)
  - `GET /api/articles/{slug}` (Get published article by slug)
  - `GET /feed.xml` (RSS feed)
- **Cache Invalidation:** Use event-driven invalidation. When an article is created, modified (published, updated), or deleted via the admin endpoints, the corresponding `fastapi-cache` namespaces (e.g., `articles:public`, `articles:{slug}`) must be cleared.
- **View Tracking Refactoring:**
  - Remove `record_view` logic from the `GET /api/articles/{slug}` endpoint.
  - Create a new, **uncached** endpoint `POST /api/articles/{slug}/view` (or similar) that accepts a client IP and records the view.
  - Update the Vue frontend to make a background `POST` request to this new endpoint upon successfully rendering an article page.
- **Auth Bypass Refactoring (Admin Previews):**
  - Remove the logic from `GET /api/articles/{slug}` that allows admins/editors to bypass the `published` status check. The public endpoint will *strictly* serve only published articles and will always be cached.
  - Create a new endpoint `GET /api/admin/articles/preview/{slug}`. This endpoint will require authentication, will *not* be cached, and will allow viewing unpublished drafts.
  - Update the Vue frontend so that the "Preview" button or routing logic for admins uses the new `GET /api/admin/articles/preview/{slug}` endpoint instead of the public one.

## Testing Decisions

- **Good Tests:** Tests should verify behavior, not implementation details. For caching, tests should verify that subsequent requests are faster or don't hit the mocked database, and that cache invalidation events correctly cause the next request to hit the database.
- **Modules to Test:**
  - Backend API caching logic (ensure `@cache` works and invalidation clears it).
  - Backend `POST /api/articles/{slug}/view` endpoint (ensure it tracks views).
  - Backend `GET /api/admin/articles/preview/{slug}` endpoint (ensure it returns drafts).
  - Frontend view tracking component/composable (ensure the POST request is fired).
  - Frontend admin preview logic (ensure it hits the correct admin endpoint).
- **Prior Art:** Existing API integration tests using `FastAPI TestClient` and Pytest fixtures. Frontend tests using Vitest and Vue Test Utils.

## Out of Scope

- Caching for admin endpoints (`/api/admin/...`).
- Caching for high-cardinality endpoints like the search API (`/api/articles/search`).
- Full page caching at the CDN level (Cloudflare/CloudFront) - this is strictly application-level API caching.
- Implementing a completely new analytics platform.

## Further Notes

- Careful attention must be paid to `fastapi-cache2` namespaces to ensure granular invalidation (e.g., invalidating a single article's cache vs. the entire list cache).
- The transition of view tracking to the client-side might result in slightly different numbers due to ad-blockers, but it's a necessary trade-off for aggressive edge/application caching.
