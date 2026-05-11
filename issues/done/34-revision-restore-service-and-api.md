## Parent

PRD: [PRD-article-revision-history.md](../prd/PRD-article-revision-history.md)

## What to build

Implement the `restore_revision()` service method and its API endpoint. Restoring a revision reverts the article's title, content, description, and tags to the state captured in that revision, while preserving workflow metadata (status, published_at, etc.). The restore action itself creates a new "restore" revision entry for auditability.

## Acceptance criteria

- [ ] `restore_revision(session, article, version_number)` in `RevisionService` restores title, content, description, and tags from the specified revision
- [ ] Restore does NOT change status, published_at, send_newsletter, or scheduled_for
- [ ] Restore does NOT change the article's slug
- [ ] After restore, a new revision entry with change_type="restore" is created capturing the restored state
- [ ] Tag names from the revision are resolved via `get_or_create_tags()` before assignment
- [ ] `POST /api/admin/articles/{article_id}/revisions/{version_number}/restore` endpoint requires admin auth
- [ ] Endpoint returns the updated article (same shape as `PUT /api/articles/{article_id}`)
- [ ] Returns 404 when article or version doesn't exist
- [ ] API tests covering: restore reverts content, restore reverts tags, restore doesn't change status/published_at, restore creates a "restore" revision entry, 404 on non-existent article/version

## Blocked by

- #31 (revision service: create + list + get)
