## Parent

PRD: [PRD-article-revision-history.md](../prd/PRD-article-revision-history.md)

## What to build

Implement the core `RevisionService` with three methods: `create_revision()`, `list_revisions()`, and `get_revision()`. This is a deep module with a simple, testable interface that encapsulates all revision snapshot and retrieval logic.

## Acceptance criteria

- [ ] `RevisionService` in `app/services/revision_service.py`
- [ ] `create_revision(session, article, change_type)` captures current article state (title, content, description, tag_names), computes next version_number (max per article + 1), and persists the revision
- [ ] `list_revisions(session, article_id)` returns revisions ordered by version_number DESC, without full content (lightweight list with version_number, change_type, title, created_at)
- [ ] `get_revision(session, article_id, version_number)` returns full revision data including content and tag_names
- [ ] Returns `None` or raises appropriate error when article_id or version_number doesn't exist
- [ ] Backend service tests in `tests/test_revision_service.py` covering: create captures correct snapshot, list returns ordered results, get returns full data, version numbers are sequential per article, non-existent article/version returns None
- [ ] Tests use SQLite in-memory pattern from `tests/conftest.py`

## Blocked by

- #30 (revision database model and migration)
