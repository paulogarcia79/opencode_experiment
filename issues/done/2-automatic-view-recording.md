# 2. Automatic View Recording on Article Fetch

## Parent

PRD: Article Performance Analytics (`prd/PRD-article-performance-analytics.md`)

## What to build

Integrate the view tracking service into the public article fetch endpoint. When a reader requests `GET /api/articles/{slug}`, the endpoint automatically records a view before returning the article. Draft articles (404 response) do not record views.

## Acceptance criteria

- [ ] `GET /api/articles/{slug}` calls `record_view()` with the article ID and IP address before returning
- [ ] IP address is currently hardcoded to `127.0.0.1` (Nginx is the entry point; real IP extraction is a follow-up)
- [ ] Draft articles do NOT record a view (404 response path skips tracking)
- [ ] Integration tests verify: view recorded for published article, no view for draft, dedup works via service
- [ ] All existing article tests continue to pass

## Blocked by

- #1 ArticleView Model + View Tracking Service
