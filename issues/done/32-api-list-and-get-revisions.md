## Parent

PRD: [PRD-article-revision-history.md](../prd/PRD-article-revision-history.md)

## What to build

Add two new admin API endpoints for listing and retrieving article revisions. These endpoints expose the revision service to the frontend.

## Acceptance criteria

- [ ] `GET /api/admin/articles/{article_id}/revisions` returns list of revisions (newest first) with version_number, change_type, title, created_at — does NOT include full content
- [ ] `GET /api/admin/articles/{article_id}/revisions/{version_number}` returns full revision data including content, description, tag_names
- [ ] Both endpoints require admin authentication (use `dependencies=[Depends(require_admin)]`)
- [ ] Returns 404 when article doesn't exist
- [ ] Returns 404 when version_number doesn't exist for the get-single endpoint
- [ ] New Pydantic schemas `RevisionRead` and `RevisionListRead` in `app/schemas.py`
- [ ] Backend API tests in `tests/test_revisions.py` covering: list returns correct order, get returns full data, 404 on non-existent article, 404 on non-existent version
- [ ] Tests use `TestClient` pattern from existing `tests/test_articles.py`

## Blocked by

- #31 (revision service: create + list + get)
