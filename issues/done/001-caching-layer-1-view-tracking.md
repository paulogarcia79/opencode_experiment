## Parent

prd/PRD-caching-layer.md

## What to build

Create a new `POST /api/articles/{slug}/view` backend endpoint to record an article view. Remove the implicit `record_view` logic from `GET /api/articles/{slug}`. Update the Vue frontend to call this new POST endpoint in the background after successfully loading an article. This decouples analytics from content delivery, paving the way for caching the GET endpoint.

## Acceptance criteria

- [ ] New `POST /api/articles/{slug}/view` endpoint exists and calls `record_view` with the client's IP.
- [ ] `GET /api/articles/{slug}` no longer calls `record_view`.
- [ ] Vue frontend (`ArticleView` or equivalent) makes a background request to the new POST endpoint when a user views an article.
- [ ] Views are still accurately tracked in the admin dashboard / database.

## Blocked by

None - can start immediately
