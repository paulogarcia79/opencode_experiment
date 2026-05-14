## Parent

prd/PRD-caching-layer.md

## What to build

Add `fastapi-cache2` and configure it in the FastAPI lifespan to use the existing Redis connection pool. Add the `@cache` decorator to `GET /api/articles`, `GET /api/articles/{slug}`, and `GET /feed.xml`. Implement event-driven cache invalidation by clearing the relevant cache namespaces whenever an article is created, updated, or deleted via the admin routes.

## Acceptance criteria

- [ ] `fastapi-cache2` is installed and initialized in `app/main.py`.
- [ ] `GET /api/articles`, `GET /api/articles/{slug}`, and `GET /feed.xml` are cached.
- [ ] Admin create/update/delete operations properly invalidate the cache.
- [ ] Subsequent requests to cached endpoints are significantly faster and bypass the database.

## Blocked by

- issues/001-caching-layer-1-view-tracking.md
- issues/001-caching-layer-2-admin-preview.md
