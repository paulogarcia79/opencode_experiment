## Parent

PRD: `prd/PRD-role-based-dashboards.md`

## What to build

Add server-side sort, filter, and role-based scoping to the admin article list endpoint. Update `GET /api/admin/articles` to accept `sort`, `order`, and `status` query params. Contributors get auto-filtered to only their own articles. Update `GET /api/admin/articles/{id}` to return 404 when a contributor requests another user's article. Write pytest tests for sort order, status filtering, and contributor scoping.

**End-to-end behavior**: An admin requests `GET /api/admin/articles?sort=title&order=asc&status=published` and gets only published articles sorted alphabetically. A contributor gets only their own articles regardless of filter. A contributor requesting another's article by ID gets 404.

## Acceptance criteria

- [ ] `GET /api/admin/articles` accepts query params: `sort` (valid column names: title, author_email, status, published_at, created_at, updated_at), `order` (asc/desc), `status` (draft/published/pending_review)
- [ ] Backend validates sort column against whitelist to prevent SQL injection
- [ ] Status filter applies `WHERE status = ?` on the query
- [ ] Sort/order applies `ORDER BY {column} {direction}` on the query
- [ ] For contributors: query auto-filters `WHERE author_id = current_user.id` regardless of other params
- [ ] `GET /api/admin/articles/{id}`: contributor requesting non-owned article returns 404 (not 403)
- [ ] Editors and admins see all articles with no auto-filter
- [ ] Backend tests (pytest): sort by each column, combined sort+filter, contributor-owned-only, contributor 404 on non-owned

## Blocked by

- Issue 1 (Backend: Models, permissions, and API hardening)
