# 1. ArticleView Model + View Tracking Service

## Parent

PRD: Article Performance Analytics (`prd/PRD-article-performance-analytics.md`)

## What to build

Create the foundational data model and service for tracking article page views. This includes a new `ArticleView` SQLModel table with IP hash deduplication, and a `view_tracking_service.py` that provides a `record_view()` function. The service adds records to the session but does NOT commit — the caller decides when to commit.

## Acceptance criteria

- [ ] `ArticleView` model created with fields: `id` (UUID), `article_id` (FK), `ip_hash` (SHA-256 string), `viewed_at` (timestamp)
- [ ] Model registered in `app/models/__init__.py` so it's included in table creation
- [ ] `view_tracking_service.py` created with `record_view(session, article_id, ip_address)` function
- [ ] Deduplication logic: no duplicate view recorded if same IP hash viewed the same article within 24 hours
- [ ] IP address is hashed with SHA-256 before storage — raw IPs are never stored
- [ ] Backend tests cover: view recording, 24h dedup, different IPs both recorded, draft article exclusion

## Blocked by

None - can start immediately
