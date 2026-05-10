# [Slice 8a] Search Backend & API

**GitHub Issue:** #008a
**Labels:** needs-triage
**State:** open

## Parent

PRD: Full-Text Search (`PRD-full-text-search.md`)

## What to build

A working full-text search backend using PostgreSQL `tsvector`. Includes the database schema (migration), search service deep module, public API endpoint, and automatic index population when articles are created or updated. The backend is independently demoable via `curl` or an API client.

## Acceptance criteria

- [ ] Alembic migration adds `search_vector tsvector` column + GIN index to `articles` table
- [ ] `Article` SQLModel includes `search_vector` field
- [ ] `extract_plain_text_from_tiptap()` reused to build searchable text on create/update
- [ ] `search_articles(session, query)` deep module: constructs `to_tsquery`, filters published, orders by `ts_rank` DESC
- [ ] Search service gracefully falls back to `LIKE` query in SQLite (test environment)
- [ ] New `GET /api/articles/search?q=term` endpoint returns `200` with relevance-ranked published articles
- [ ] Endpoint returns `400 Bad Request` if `q` is missing or empty after trimming
- [ ] On article create/update, `search_vector` is populated automatically
- [ ] Existing articles get `search_vector` backfilled via migration or startup script
- [ ] Backend tests: search finds by title, by description, by content; excludes drafts; ranks relevance; validates 400 on empty query

## Blocked by

None - can start immediately
