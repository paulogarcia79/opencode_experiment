# PRD: Article Tags

## Problem Statement

Readers browsing the blog have no way to discover related content beyond chronological scrolling and full-text search. Articles about similar topics (e.g., multiple Docker tutorials, several game design essays) are scattered across the timeline with no connective tissue. The admin has no way to organize content thematically, which limits the blog's usefulness as a reference resource and reduces reader engagement.

## Solution

Add a lightweight tag taxonomy system. Articles can be tagged with free-form labels (e.g., "docker", "game-design", "tutorial"). Tags are displayed as plain-text badges on article detail pages and are clickable to a `/tags/:slug` page listing all articles with that tag. Tags are created inline via a hybrid autocomplete input in the article editor — existing tags are suggested as the admin types, and new tags are created on Enter. A dedicated `/admin/tags` page allows tag management (view article counts, delete with confirmation). Tags are included in full-text search so that searching "docker" finds articles tagged "docker" even if the word doesn't appear in the body.

## User Stories

1. As a reader, I want to see tags on an article's detail page, so that I can quickly understand what topics it covers
2. As a reader, I want to click a tag and see all articles with that tag, so that I can explore related content
3. As a reader, I want tags included in full-text search, so that searching for a topic finds articles tagged with that topic even if the word doesn't appear in the text
4. As a site owner, I want to tag articles while editing them, so that I can organize content thematically for readers
5. As a site owner, I want tag suggestions as I type, so that I don't accidentally create duplicate tags with different casing
6. As a site owner, I want to create new tags inline without leaving the article editor, so that the tagging workflow doesn't interrupt writing
7. As a site owner, I want a limit on how many tags an article can have, so that tag lists stay focused and don't become keyword spam
8. As a site owner, I want a tags admin page, so that I can see all tags, their usage counts, and clean up unused or mistyped tags
9. As a site owner, I want a warning before deleting a tag that is in use, so that I don't accidentally detach tags from articles
10. As a developer, I want tag associations to be eagerly loaded with article responses, so that the frontend doesn't need extra requests to display tags
11. As a developer, I want tags to use SQLModel's Relationship pattern, so that the code is idiomatic and tag access feels natural (`article.tags`)
12. As a developer, I want tag slugs to be auto-generated from names, so that URL-safe identifiers are consistent and don't require manual entry

## Implementation Decisions

### Modules

**Tag Model**
- `Tag` SQLModel with `id` (UUID PK), `name` (unique, case-insensitive), `slug` (unique, immutable, auto-generated), `created_at`
- Auto-generated slug: lowercase, spaces to hyphens, deduplicated with counter suffix if collision occurs
- `Article` model gains `tags: List[Tag] = Relationship(link_model=ArticleTag, ...)` using SQLModel's `Relationship` pattern

**ArticleTag Link Model**
- Simple link table: `article_id` (FK → articles.id), `tag_id` (FK → tags.id), composite PK on both columns
- Follows the same FK pattern as `newsletter_sends` but uses `Relationship(link_model=...)` for ORM-level access

**Tag Service (Deep Module)**
- `get_or_create_tags(session, names: list[str]) -> list[Tag]` — case-insensitive lookup, creates missing tags, returns all matched/created tags
- `delete_tag(session, tag_id)` — checks article count, warns if in use, removes associations and tag
- `list_tags(session)` — returns all tags with article counts
- `list_articles_by_tag(session, slug)` — returns published articles for a tag slug, eager-loaded with tags

**Article Service Update**
- `create_article` and `update_article` accept an optional `tag_names: list[str]` parameter
- Calls `get_or_create_tags()` to resolve names to Tag objects
- Assigns tags to the article via `article.tags = tags`
- Rebuilds `search_text` to include tag names concatenated with title, description, and content

**Tag Admin Endpoints**
- `GET /api/admin/tags` — list all tags with article count
- `POST /api/admin/tags` — create a new tag (used by autocomplete when inline creation is needed, though most tags are created via article endpoints)
- `DELETE /api/admin/tags/{tag_id}` — delete tag; returns `409 Conflict` with article count if tag is in use (frontend shows warning)

**Public Tag Endpoints**
- `GET /api/tags` — list all tags with article counts (for potential tag index page later)
- `GET /api/tags/{slug}` — get single tag with its articles
- `GET /api/tags/{slug}/articles` — list published articles for tag, eager-loaded with tags

**Article Endpoint Updates**
- `GET /api/articles` and `GET /api/articles/{slug}` and `GET /api/admin/articles/*` eager-load tags via `selectinload`
- `POST /api/admin/articles` and `PUT /api/articles/{id}` accept `tag_names` in the payload
- Response shape includes `tags: list[{name, slug}]` on all article responses

**Frontend Tag Composable**
- `useTags()` — fetches tag list, provides CRUD operations
- `useTagSearch()` — debounced fetch of tag suggestions for the autocomplete input

**Tag Input Component**
- Multi-select chip input with autocomplete dropdown
- Shows existing tag suggestions as admin types (debounced 150ms)
- Enter or click creates/accepts a tag
- Hard cap at 8 tags — input disables once limit reached
- Tags rendered as removable chips inside the input

**Tag Admin Page (`/admin/tags`)**
- Table view: name, slug, article count, created_at
- Delete button per tag with confirmation dialog
- Dialog shows "This tag is used by N articles. Deleting it will remove the tag from those articles."

**Article Detail Page Update**
- Tag badges rendered as plain-text pills below the article metadata row
- Each badge is a `RouterLink` to `/tags/:slug`
- Styled consistently with dark tech aesthetic (bordered pills, no background color changes)

**Tag Articles Page (`/tags/:slug`)**
- New route and view component
- Header shows tag name and article count
- Article list reuses `HomeView.vue` card styling exactly
- Empty state if tag has no published articles

### Schema Changes

- New `tags` table: `id` (UUID PK), `name` (String, unique, case-insensitive index), `slug` (String, unique, index), `created_at` (DateTime)
- New `article_tags` link table: `article_id` (UUID, FK → articles.id), `tag_id` (UUID, FK → tags.id), composite PK
- Alembic migration adds both tables and applies unique constraints

### API Contracts

- `POST /api/admin/articles` — accepts `tag_names: list[str]` (optional, max 8)
- `PUT /api/articles/{id}` — accepts `tag_names: list[str]` (optional, replaces existing tags)
- All article GET responses include `tags: list[{name: str, slug: str}]`
- `DELETE /api/admin/tags/{id}` — returns `409` with `{detail: str, article_count: int}` if tag has articles

### Case Sensitivity

- Tag names are case-insensitive for lookup and deduplication
- First-used casing is preserved as the display `name`
- Slug is always lowercase

## Testing Decisions

**What makes a good test:** Test behavior through public interfaces. For the backend, verify that tagging an article returns the tag in the response, that searching finds tagged articles, and that tag deletion respects the warning. For the frontend, verify that the tag input renders chips, that autocomplete suggests existing tags, and that the tag page lists articles. Do not test internal slug generation or SQLModel relationship internals directly.

**Modules to test:**
- Tag service: verify `get_or_create_tags` is case-insensitive, verify slug generation, verify delete with articles blocks, verify delete without articles succeeds
- Article endpoints: verify create with tags includes tags in response, verify update replaces tags, verify max 8 tag validation, verify tag names appear in search results
- Tag endpoints: verify list includes article counts, verify delete returns 409 when in use, verify 204 when unused
- Frontend tag input component: verify typing shows suggestions, verify Enter creates chip, verify max 8 disables input, verify backspace removes chip
- Tag admin page: verify table renders tags with counts, verify delete shows confirmation dialog
- Article detail page: verify tag badges render and link to tag page
- Tag articles page: verify articles for tag render, verify empty state

**Prior art:**
- Backend tests use `TestClient` + `session` fixtures (see `test_articles.py` for endpoint testing, `test_search.py` for search behavior patterns)
- Frontend tests use `@vue/test-utils` with `flushPromises` for async behavior (see `AdminMediaView.spec.ts` for table/list testing, `ShareButtons.spec.ts` for component interaction)

## Out of Scope

- Tag colors or visual customization — plain text badges only
- Tag descriptions or metadata beyond name/slug
- Hierarchical categories or nested tags
- Tag-based RSS feed or sitemap entries
- Tag analytics (most popular tags, tag trend graphs)
- Tag renaming after creation (slugs are immutable)
- Article-level tag ordering or primary tag designation
- Tag cloud / sidebar widget on homepage
- Tag autocomplete in the public site search bar
- Tag-based subscriber segmentation for newsletters

## Further Notes

- This is the first use of SQLModel `Relationship` in the codebase. All previous relationships (e.g., `newsletter_sends` → `articles`/`subscribers`) used manual foreign keys with explicit `select()` joins. Tags will establish the `Relationship` pattern as the new standard.
- The `search_text` column on `articles` must be rebuilt when tags change, just as it is when title/description/content change. The existing `build_search_text()` utility should concatenate tag names.
- Tag slugs follow the same generation logic as article slugs (lowercase, hyphenate, deduplicate with counter). Consider extracting a shared `slugify()` utility if one doesn't exist.
- The 8-tag hard cap is enforced in both frontend (input disables) and backend (schema validation) to prevent abuse.
