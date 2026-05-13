# Issue 45: Article Reassignment

## Parent

Issue #38: Multi-author Support

## What to build

Allow editors and admins to reassign article ownership from one user to another. Add a `PUT /api/admin/articles/{id}/reassign` endpoint that changes the `author_id`, creates a revision with `change_type="reassign"` capturing old and new author, and returns the updated article. In the frontend, add a "Change Author" dropdown to the article edit view (visible only to editors/admins) listing all active users.

## Acceptance criteria

- [ ] `PUT /api/admin/articles/{id}/reassign` accepts `{ author_id }`, updates article author (editor/admin only)
- [ ] Reassign endpoint returns 404 if article not found
- [ ] Reassign endpoint returns 403 for contributors
- [ ] Reassign endpoint returns 400 if target user doesn't exist or is inactive
- [ ] Reassign creates an `ArticleRevision` with `change_type="reassign"` and metadata about old/new author
- [ ] `AdminArticleEditView.vue` shows "Change Author" dropdown for editors/admins only
- [ ] Dropdown lists all active users with email display
- [ ] Reassignment shows confirmation dialog before executing
- [ ] Success/error messages displayed after reassignment attempt
- [ ] Tests for reassign endpoint (success, 403, 404, 400 cases)
- [ ] Tests verify revision is created with correct change_type
- [ ] Tests for frontend dropdown visibility (hidden for contributors, visible for editors/admins)

## Blocked by

- Issue #40: Article Ownership + Author Display
- Issue #41: Auth Me Endpoint + Frontend Role Store
