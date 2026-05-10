# [Slice 8] Full-Text Search

**GitHub Issue:** #008
**Labels:** needs-triage
**State:** open

## Parent

PRD: Full-Text Search (`PRD-full-text-search.md`)

## What to build

Add full-text search across published articles using PostgreSQL `tsvector`. Readers can search by title, description, and article body content via a search input in the header, with results displayed on a dedicated `/search` page. Search triggers after a 300ms debounce and results are ranked by relevance.

## Acceptance criteria

- [ ] `Article` model gains `search_vector` column (type `tsvector`)
- [ ] Alembic migration adds `search_vector` column + GIN index
- [ ] On article create/update, `search_vector` is populated from `title + description + plain_text(content)`
- [ ] New `GET /api/articles/search?q=term` endpoint returns published articles ordered by relevance
- [ ] Search endpoint returns `400` if `q` is missing or empty
- [ ] Search service is a deep module with simple interface: `search_articles(session, query) -> list[Article]`
- [ ] Search endpoint only returns `published` articles
- [ ] Frontend search composable handles debounced fetch (300ms), loading state, error state
- [ ] Search input in header navigates to `/search?q=term` on submit
- [ ] Dedicated `/search` page renders results as article cards with loading skeleton and empty state
- [ ] Backend tests: verify search by title, by content, excludes drafts, ranks relevance
- [ ] Frontend tests: verify debounced fetch, results render, empty state, loading state

## Blocked by

None - can start immediately
