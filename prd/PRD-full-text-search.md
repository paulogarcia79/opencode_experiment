## Problem Statement

Readers cannot search for articles on the blog. As the article count grows, browsing the chronological list becomes inefficient. There is no way for a reader to find articles about specific topics (e.g., "docker", "game design", "vue 3") without manually scrolling through the entire archive. This limits content discoverability and reduces repeat visits from readers looking for reference material.

## Solution

Add full-text search across all published articles. A search input in the site header navigates to a dedicated `/search` page. As the user types, results update after a 300ms debounce, showing articles ranked by relevance (title matches rank highest, followed by description, then body content). Each result card shows the article title, description, and publish date — styled consistently with the existing dark tech aesthetic.

## User Stories

1. As a reader, I want to type a keyword into a search input and see matching articles, so that I can quickly find content on a specific topic
2. As a reader, I want search results to update as I type, so that I can iterate my query without waiting for a page reload
3. As a reader, I want search results ordered by relevance, so that the most pertinent articles appear first
4. As a reader, I want the search page to show a loading state while results are fetched, so that I know the system is working
5. As a reader, I want a clear empty state when no articles match my query, so that I know to try different keywords
6. As a reader, I want search to only include published articles, so that I never see drafts or unfinished content
7. As a site owner, I want search to match partial words via PostgreSQL stemming, so that "running" finds articles about "run"
8. As a developer, I want the search index to stay in sync when articles are created or updated, so that results are always accurate
9. As a developer, I want the search endpoint to accept a simple `?q=` query parameter, so that the API is easy to consume from the frontend
10. As a developer, I want the search service to be a deep module with a simple interface, so that it can be tested in isolation and reused elsewhere

## Implementation Decisions

### Modules

**Search Service**
- A deep module with a single public function: `search_articles(session, query: str) -> list[Article]`
- Internally constructs a `to_tsquery('english', query)` from user input
- Filters articles by `status == "published"` and `search_vector @@ query`
- Orders results by `ts_rank(search_vector, query) DESC`
- Hides all PostgreSQL `tsvector` / `tsquery` complexity behind this interface

**Search Endpoint**
- New public endpoint: `GET /api/articles/search?q=term`
- Returns `400` if `q` is missing or empty after trimming
- Returns `200` with a list of `Article` response models ordered by relevance
- Reuses the existing `Article` SQLModel for both query and response

**Article Model Update**
- Add a `search_vector` column of type `tsvector` to the `Article` SQLModel
- The column is populated application-side (not a database-generated column) because `content` is stored as TipTap JSON and requires Python-side plain-text extraction
- On article create and update, extract plain text from TipTap JSON using the existing `extract_plain_text_from_tiptap()` utility, concatenate with `title` and `description`, and store as `to_tsvector('english', ...)`

**Frontend Search Composable**
- Encapsulates debounced fetch logic (300ms), loading state, error state, and result caching
- Exposes: `query`, `results`, `loading`, `error`, `search(term)`
- Deep module: simple interface hiding debounce, fetch, and state management

**Search View**
- Dedicated `/search` route and page component
- Contains a prominent search input (pre-filled from URL `?q=` parameter)
- Renders results as article cards matching the existing homepage card style
- Shows loading skeleton state and themed empty state

**Header Search Input**
- Compact search icon in the site header that expands to an input on click/focus
- Navigates to `/search?q=term` on submit (Enter key)
- Present on both homepage and article detail pages

### Schema Changes

- Add `search_vector: tsvector` column to the `articles` table via Alembic migration
- Add a functional GIN index on `search_vector` for fast `@@` queries

### API Contract

- `GET /api/articles/search?q=term`
  - Query param `q` (required, non-empty string)
  - Response: `200 OK`, `list[Article]` ordered by relevance descending
  - Error: `400 Bad Request` if `q` missing or empty

### Query Behavior

- Uses PostgreSQL `to_tsquery('english', query)` with plainto_tsquery for user input
- Accepts PostgreSQL defaults: case-insensitive, English stemming, word boundaries
- No prefix matching (`:*`) for now — can be added later if needed

## Testing Decisions

**What makes a good test:** Test behavior through public interfaces. For the backend, verify that the search endpoint returns the correct articles for a query and excludes drafts. For the frontend, verify that typing in the search input triggers a debounced fetch and that results render correctly. Do not test internal `tsvector` construction or debounce timing directly.

**Modules to test:**
- Search service: verify it finds articles by title, by description, by content; verify it excludes drafts; verify it ranks title matches above content matches
- Search endpoint: verify 200 with results, verify 400 when `q` is missing, verify only published articles returned
- Frontend search composable: verify debounced fetch, verify loading state toggles, verify error handling
- Search view component: verify input pre-fills from URL, verify results render, verify empty state, verify loading state

**Prior art:**
- Backend tests use `TestClient` + `session` fixtures (see `test_articles.py` for endpoint testing patterns)
- Frontend tests use `@vue/test-utils` with `flushPromises` for async behavior (see `AdminMediaView.spec.ts` and `ShareButtons.spec.ts`)

## Out of Scope

- Prefix matching (`:*`) in `to_tsquery` — deferred to a future enhancement if users request partial-word matching
- Search result highlighting (highlighting matched terms in titles/descriptions) — nice-to-have but adds complexity
- Faceted search or filters (by date range, tag, author) — requires additional schema and UI work
- Search analytics (tracking what users search for) — purely operational, no code needed
- Autocomplete / search suggestions — can be added later as a separate feature
- Searching subscribers, images, or other entity types — out of scope for article search

## Further Notes

- The existing `content_service.py` has `extract_plain_text_from_tiptap()` which should be reused for populating `search_vector`
- SQLite (used in tests) does not support `tsvector`; the search service should gracefully fall back to a `LIKE` query when `tsvector` is unavailable, or tests should mock the search behavior
- The GIN index on `search_vector` is critical for performance as article count grows; without it, full-text queries become table scans
- Consider updating `search_vector` asynchronously via a background job if article update frequency becomes high enough that synchronous extraction causes latency
