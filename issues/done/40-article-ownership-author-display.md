# Issue 40: Article Ownership + Author Display

## Parent

Issue #38: Multi-author Support

## What to build

Add article ownership tracking by adding an `author_id` foreign key to the `Article` model, set the author automatically on article creation, and display the author name/email in the admin articles list. Also update the revision service to capture the `author_id` on explicit save/publish, and update the revision panel UI to show who made each change.

## Acceptance criteria

- [ ] `Article` model has `author_id: uuid.UUID` foreign key referencing `User.id` (nullable for migration backfill)
- [ ] `Article` model has `author` relationship for eager loading
- [ ] Alembic migration adds the column and backfills existing articles to the first admin user
- [ ] Article creation endpoints (`POST /api/admin/articles`, autosave) set `author_id` from the authenticated user
- [ ] `ArticleRevision` model has `author_id: uuid.UUID` (nullable) field
- [ ] Revision creation on explicit save/publish captures current user's ID
- [ ] Auto-save revisions continue to exclude author (existing behavior preserved)
- [ ] Admin articles list API response includes author email/name
- [ ] `AdminArticlesView.vue` displays author column in the table
- [ ] Revision panel (`RevisionPanel.vue`) displays author email next to timestamp
- [ ] Frontend `Article` type updated to include `author` field
- [ ] Tests for article creation verify author is set correctly
- [ ] Tests for revision creation verify author is captured

## Blocked by

- Issue #39: Role Model Migration + Permission Service
