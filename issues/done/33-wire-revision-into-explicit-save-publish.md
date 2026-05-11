## Parent

PRD: [PRD-article-revision-history.md](../prd/PRD-article-revision-history.md)

## What to build

Wire revision creation into the existing article update endpoint so that every explicit save or publish creates a revision snapshot. Auto-save endpoints must NOT create revisions.

## Acceptance criteria

- [ ] `PUT /api/articles/{article_id}` calls `create_revision(session, article, "publish")` when status changes from draft to published
- [ ] `PUT /api/articles/{article_id}` calls `create_revision(session, article, "save")` for all other explicit saves
- [ ] Revision is created BEFORE the article is updated, so the snapshot captures the previous state
- [ ] `PUT /api/admin/articles/{article_id}/autosave` does NOT create a revision (verify with test)
- [ ] `POST /api/admin/articles/autosave` does NOT create a revision (verify with test)
- [ ] API tests in `tests/test_revisions.py` covering: revision created on save, revision created on publish with change_type="publish", no revision on auto-save, revision captures pre-update state
- [ ] Existing article tests continue to pass

## Blocked by

- #31 (revision service: create + list + get)
