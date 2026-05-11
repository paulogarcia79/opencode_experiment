# PRD: Article Revision History

## Problem Statement

As an admin editor, I can accidentally overwrite good content when updating an article, and I have no way to see what changed between edits or restore a previous version. The current system overwrites articles in place on every save, with only an `updated_at` timestamp to show that *something* changed. I need a revision history so I can track changes over time and roll back to a previous version if needed.

## Solution

Add a revision history system that captures a full snapshot of article content (title, description, TipTap content, and tags) every time an admin explicitly saves or publishes an article. Provide an API to list, view, and restore revisions, and a slide-out panel in the article editor that shows a diff view of each revision so I can compare and restore with confidence.

## User Stories

1. As an admin editor, I want every explicit save of an article to create a revision snapshot, so that I have a history of all meaningful changes.
2. As an admin editor, I want publishing an article to create a revision marked as "publish", so that I can distinguish between draft saves and published versions.
3. As an admin editor, I want to see a list of all revisions for an article in chronological order, so that I can browse the history of changes.
4. As an admin editor, I want each revision in the list to show the version number, timestamp, change type (save/publish), and title, so that I can quickly identify the revision I'm looking for.
5. As an admin editor, I want to view a single revision's full content, so that I can preview what the article looked like at that point.
6. As an admin editor, I want to see a diff between the current article and a previous revision, so that I can understand exactly what changed.
7. As an admin editor, I want the diff to highlight changes in the title and description at the character level, so that I can see small text edits clearly.
8. As an admin editor, I want the diff to show a word-level plain text comparison of the TipTap content, so that I can see what content was added or removed.
9. As an admin editor, I want to restore an article to a previous revision, so that I can undo unwanted changes.
10. As an admin editor, I want restoring a revision to also restore the article's tags to their previous state, so that the full content identity is recovered.
11. As an admin editor, I want restoring a revision to create a new revision entry (marked as "restore"), so that the restore action itself is tracked in history.
12. As an admin editor, I want auto-save operations to NOT create revisions, so that the revision history isn't cluttered with hundreds of incremental drafts.
13. As an admin editor, I want the revision history panel to be a slide-out on the right side of the article editor, so that I can review history without losing my editing context.
14. As an admin editor, I want to see a "History" button in the editor toolbar, so that I can easily open the revision panel.
15. As an admin editor, I want the restore action to require confirmation, so that I don't accidentally overwrite my current draft.

## Implementation Decisions

### Database Schema
- A new `ArticleRevision` SQLModel table with columns:
  - `id` (UUID, primary key)
  - `article_id` (UUID, foreign key to `articles.id`, indexed)
  - `version_number` (integer, per-article auto-increment)
  - `title` (string, snapshot)
  - `content` (JSON, TipTap document snapshot)
  - `description` (text, nullable, snapshot)
  - `tag_names` (JSON array of strings, snapshot)
  - `change_type` (string: "save", "publish", or "restore")
  - `created_at` (datetime)
- An Alembic migration will create this table.
- `version_number` is scoped per article (max version per article + 1 on insert).

### Backend Modules
- **New model:** `ArticleRevision` in `app/models/article_revision.py`
- **New service:** `RevisionService` in `app/services/revision_service.py` with a clean interface:
  - `create_revision(session, article, change_type)` — captures current state, assigns next version number
  - `list_revisions(session, article_id)` — returns revisions ordered by version_number DESC, without full content (lightweight list)
  - `get_revision(session, article_id, version_number)` — returns full revision data
  - `restore_revision(session, article, version_number)` — restores article content from revision, creates a new "restore" revision entry
- **Modified service:** `article_service.update_article()` will call `create_revision()` before applying updates when the update comes from an explicit save (not auto-save).
- **New Pydantic schemas:** `RevisionRead`, `RevisionListRead` in `app/schemas.py`
- **New API endpoints** (all admin-authenticated):
  - `GET /api/admin/articles/{article_id}/revisions` — list revisions (lightweight, no content)
  - `GET /api/admin/articles/{article_id}/revisions/{version_number}` — get full revision
  - `POST /api/admin/articles/{article_id}/revisions/{version_number}/restore` — restore revision
- **Modified endpoint:** `PUT /api/articles/{article_id}` (update) will call `create_revision(session, article, "save")` or `create_revision(session, article, "publish")` before applying the update, depending on whether the status is changing to "published".
- **Auto-save endpoints will NOT create revisions.** They remain unchanged.

### Diff Logic
- A new utility function `compute_diff(old_text, new_text)` in `app/services/diff_service.py` that returns a structured diff (list of added/removed/unchanged segments).
- Uses a simple longest-common-subsequence or word-level diff algorithm (Python's `difflib` is sufficient).
- For title and description: character-level inline diff.
- For TipTap content: extract plain text via existing `extract_plain_text_from_tiptap()`, then word-level diff.
- The diff is computed on-demand by the API when fetching a single revision, or by the frontend — we'll compute it in the **frontend** to keep the API simple. The API returns the raw revision content; the frontend computes the diff using a JS diff library (e.g., `diff` npm package).

### Frontend Modules
- **New composable:** `useRevisions(articleId)` in `frontend/src/composables/useRevisions.ts` — fetches revision list, fetches single revision, triggers restore.
- **New component:** `RevisionPanel.vue` in `frontend/src/components/RevisionPanel.vue` — slide-out panel showing revision timeline, diff view, and restore button.
- **Modified component:** `AdminArticleEditView.vue` — adds a "History" button that toggles the `RevisionPanel` slide-out.
- **Diff rendering:** Uses the `diff` npm package for word-level/character-level diff computation in the browser. Renders diffs with green (added) and red (removed) inline highlighting.
- The slide-out panel overlays the right side of the editor, pushing content left or using a fixed-position overlay.

### API Contracts
- `GET /api/admin/articles/{article_id}/revisions` returns:
  ```json
  [
    { "version_number": 3, "change_type": "publish", "title": "My Article", "created_at": "2025-01-15T10:30:00" },
    { "version_number": 2, "change_type": "save", "title": "My Article (draft)", "created_at": "2025-01-15T09:00:00" }
  ]
  ```
- `GET /api/admin/articles/{article_id}/revisions/{version_number}` returns:
  ```json
  {
    "version_number": 2,
    "change_type": "save",
    "title": "My Article (draft)",
    "content": { "type": "doc", "content": [...] },
    "description": "A brief description",
    "tag_names": ["tech", "python"],
    "created_at": "2025-01-15T09:00:00"
  }
  ```
- `POST /api/admin/articles/{article_id}/revisions/{version_number}/restore` returns the updated article (same shape as `PUT /api/articles/{article_id}`).

### Tag Handling on Restore
- The `tag_names` stored in the revision are resolved via the existing `get_or_create_tags()` service on restore, then assigned to the article — the same pattern `update_article()` already uses.

### Restoration Behavior
- Restoring a revision updates `title`, `content`, `description`, and `tags` on the article.
- It does **not** change `status`, `published_at`, `send_newsletter`, or `scheduled_for`.
- A new revision entry with `change_type="restore"` is created after the restore, capturing the restored state so the action is auditable.
- The article's `slug` is **not** changed on restore (slug is tied to the original article identity).

## Testing Decisions

### What Makes a Good Test
- Test external behavior through the API (HTTP request/response), not internal service method calls.
- Test the full lifecycle: create article → update (creates revision) → list revisions → restore → verify article state.
- Use the existing `TestClient` + SQLite in-memory pattern from `tests/conftest.py`.

### Modules to Test
- **Backend API tests** (new file `tests/test_revisions.py`):
  - Creating a revision on explicit save (`PUT /api/articles/{id}`)
  - Creating a revision on publish (status change to "published")
  - No revision created on auto-save (`PUT /api/admin/articles/{id}/autosave`)
  - `GET /api/admin/articles/{id}/revisions` returns correct list, newest first
  - `GET /api/admin/articles/{id}/revisions/{version}` returns full data
  - `POST /api/admin/articles/{id}/revisions/{version}/restore` restores content and creates a "restore" revision
  - Restore does not change `status` or `published_at`
  - Restore correctly reassigns tags via `get_or_create_tags()`
  - 404 on non-existent article or non-existent version
  - Version numbers are sequential per article
- **Backend service tests** (new file `tests/test_revision_service.py`):
  - `create_revision` captures correct snapshot
  - `list_revisions` returns ordered results
  - `restore_revision` applies content correctly
- **Frontend tests** (new file `frontend/src/composables/__tests__/useRevisions.test.ts`):
  - `useRevisions` fetches revision list correctly
  - `useRevisions.restore()` calls the correct API endpoint
- **Prior art:** `tests/test_articles.py` for backend API test patterns, `frontend/src/composables/__tests__/useAdminApi.test.ts` for frontend composable test patterns.

## Out of Scope

- Diff computation on the backend (done in the frontend for simplicity).
- Revision notes or comments (no free-text annotations on revisions).
- Branching/forking revisions (linear history only).
- Comparing two arbitrary revisions side-by-side (only current vs. selected revision).
- Revision deletion or pruning (all revisions are permanent).
- Multi-author attribution (revisions are not attributed to specific users yet — single admin model).
- Markdown import or export of revisions.
- Revision history for tags admin operations (only article content revisions).

## Further Notes

- The `ArticleRevision` model follows the same SQLModel patterns as the existing codebase (UUID primary keys, relationship to Article).
- The revision service is designed as a deep module: simple interface (`create`, `list`, `get`, `restore`) encapsulating all the snapshot/restore logic. This makes it easy to test in isolation and unlikely to need interface changes.
- The frontend diff computation uses the `diff` npm package, which is a well-maintained, standard choice for JS diff operations. This avoids adding backend complexity for a UI-only concern.
- Future: if revision history grows large, we could add pagination to the list endpoint or archive old revisions. Not needed for initial implementation.
