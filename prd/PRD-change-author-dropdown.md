## Problem Statement

As an admin, I need to reassign articles between authors when team members leave or content ownership changes, but there's no UI for this in the article edit view. The backend endpoint exists (`PUT /api/admin/articles/{id}/reassign`), but I have to use the API directly or a database client to reassign articles. The QA checklist expects a "Change Author" dropdown that doesn't exist.

## Solution

Add a "Change Author" dropdown to the article edit view that is visible only to admins. It allows selecting a different author from a list of active users and triggers the existing reassign endpoint with a confirmation dialog.

## User Stories

1. As an admin, I want to see a "Change Author" dropdown in the article edit view so that I can reassign article ownership without using the API directly
2. As an admin, I want to select a new author from a dropdown of active users so that I can quickly reassign articles
3. As an admin, I want to see a confirmation dialog before reassigning so that I don't accidentally change ownership
4. As an admin, I want to see a success message after reassignment so that I know the operation completed
5. As an admin, I want the article author to update immediately in the UI after reassignment so that I see the change reflected
6. As an editor, I should not see the "Change Author" dropdown so that I don't attempt actions I'm not allowed to do
7. As a contributor, I should not see the "Change Author" dropdown so that I don't attempt actions I'm not allowed to do
8. As any role, I want the reassignment to create a revision with `change_type: "reassign"` so that the ownership change is tracked in history

## Implementation Decisions

- **AdminArticleEditView**: Add a "Change Author" section visible only when `user.role === 'admin'`
- **User list**: Fetch active users via existing `GET /api/admin/users` endpoint (already available in `useAdminApi.ts`)
- **Dropdown**: Native `<select>` element styled to match existing UI, populated with active users (email as label, UUID as value)
- **Confirmation**: Use `window.confirm()` for simplicity, matching existing patterns (delete confirmation, toggle active confirmation)
- **API call**: Call existing `PUT /api/admin/articles/{id}/reassign` endpoint with `{ author_id: selectedUserId }`
- **Post-reassignment**: Refresh article data to update the displayed author, show success message
- **Error handling**: Display error message if reassignment fails (e.g., invalid user, inactive user)
- **Deep module extraction**: Extract a `reassignArticle` function in `useAdminApi.ts` if not already present (check existing API composable)
- **No backend changes needed** — the reassign endpoint is fully implemented and tested

## Testing Decisions

- **Frontend tests only** — no backend changes
- **AdminArticleEditView**: Test that "Change Author" dropdown is visible for admins, hidden for editors/contributors. Test that selecting a user and confirming triggers the reassign API call. Test that error states display correctly.
- **Prior art**: Existing frontend tests in `frontend/src/views/__tests__/` use Vitest + `@vue/test-utils`. The `AdminUsersView` tests show patterns for API interaction testing.
- **Backend tests already exist** for the reassign endpoint in `tests/test_article_reassignment.py` — no new backend tests needed.

## Out of Scope

- Backend reassign endpoint changes (already implemented)
- Bulk reassignment of multiple articles
- Reassignment history UI beyond the existing revision panel
- Email notification to old/new author on reassignment
- Role-based filtering of the user dropdown (shows all active users)

## Further Notes

- The existing `reassignArticle` service in `app/services/article_service.py` already handles: validating the target user exists and is active, updating `author_id`, creating a revision with `change_type: "reassign"` and `reassign_metadata` containing old/new author IDs.
- The revision panel already displays reassign revisions with metadata — no changes needed there.
- The QA checklist item on line 79 incorrectly states editors should see the "Change Author" dropdown. This should be admin-only per the implementation decisions.
