## Parent

PRD: `prd/PRD-change-author-dropdown.md`

## What to build

Add a "Change Author" dropdown to the article edit view that is visible only to admins. It fetches the list of active users, allows selecting a new author, confirms the action, and calls the existing backend reassign endpoint. After success, the UI updates to reflect the new author.

## Acceptance criteria

- [ ] `reassignArticle(articleId, authorId)` function added to `useAdminApi.ts` calling `PUT /api/admin/articles/{id}/reassign`
- [ ] "Change Author" section added to `AdminArticleEditView.vue`, visible only when `user.role === 'admin'`
- [ ] Dropdown populated with active users (email as label, UUID as value), fetched via existing `fetchUsers()`
- [ ] Selecting a different author triggers `window.confirm()` before calling the API
- [ ] On success: success message displayed, article author updated in UI
- [ ] On error: error message displayed (e.g., target user inactive, API failure)
- [ ] Dropdown hidden for editors and contributors
- [ ] Frontend test: dropdown visible for admin, hidden for editor/contributor
- [ ] Frontend test: selecting user and confirming calls `reassignArticle` with correct payload
- [ ] Frontend test: error state displays correctly when API returns 400

## Blocked by

None - can start immediately
