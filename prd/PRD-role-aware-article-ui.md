## Problem Statement

As a contributor, I see Edit and Delete buttons on all articles in the admin list, but clicking Edit on articles I don't own causes the autosave API call to fail with a permission error. The publish toggle is visible but non-functional for contributors. This creates a confusing experience where the UI suggests capabilities that the backend correctly blocks.

## Solution

Make the frontend UI aware of the user's role and article ownership, so contributors only see actions they can actually perform. Contributors still see all articles in the list for transparency, but action buttons are filtered based on what they're allowed to do.

## User Stories

1. As a contributor, I want to see all articles in the admin list so that I can reference what others are working on
2. As a contributor, I want to see an Edit button only on articles I own so that I don't attempt to edit articles I can't modify
3. As a contributor, I want to see a "View Only" indicator on articles I don't own so that I understand why I can't edit them
4. As a contributor, I should not see a Delete button on any article so that I don't attempt actions I'm not allowed to do
5. As a contributor, I should not see the "Publish immediately" toggle when editing my own article so that I don't attempt to publish (which I'm not allowed to do)
6. As a contributor, I should not see the "Send newsletter" checkbox when editing my own article so that I don't attempt to send newsletters (which I'm not allowed to do)
7. As a contributor, when I try to navigate to edit an article I don't own, I should be redirected to the articles list with an error message so that I understand I don't have permission
8. As a contributor, when I create a new article, autosave should work correctly so that my draft is saved without errors
9. As an editor, I want to see Edit and Delete buttons on all articles so that I can manage any article
10. As an editor, I want to see the publish toggle and newsletter checkbox so that I can publish articles and send newsletters
11. As an admin, I want to see all controls including the "Change Author" dropdown so that I can manage articles and reassign them
12. As any role, I want the UI to reflect my actual permissions so that I don't encounter confusing API errors

## Implementation Decisions

- **Permission source of truth**: The frontend will use the `useAdminStore` to get the current user's `role` and `id`. The `PERMISSIONS` dict in `permission_service.py` remains the backend source of truth.
- **Article ownership check**: Frontend will compare `article.author?.id` with `user.id` from the Pinia store to determine ownership for the `edit_own` permission.
- **AdminArticlesView**:
  - Import `useAdminStore` to access `user.role` and `user.id`
  - Conditionally render Edit/Delete buttons based on role and ownership
  - Contributors: Edit visible only on owned articles, Delete hidden entirely
  - Add a "View Only" badge in the actions column for articles contributors can't edit
- **AdminArticleEditView**:
  - On mount, if contributor is editing an article where `article.author?.id !== user.id`, redirect to `/admin` with an error message
  - Hide "Publish immediately" toggle for contributors (always submit `status: 'draft'`)
  - Hide "Send newsletter" checkbox for contributors
  - Autosave works unchanged — backend already sets `author_id` on creation, so subsequent autosaves for owned articles succeed
- **No backend changes needed** — the permission enforcement is already correct. This PR is purely frontend UI alignment.
- **Deep module extraction**: The permission-checking logic will be extracted into a composable `useArticlePermissions(article)` that returns `{ canEdit, canDelete, canPublish }` based on the current user's role and article ownership. This encapsulates the permission logic in one place and is easily testable.

## Testing Decisions

- **Frontend tests only** — no backend changes
- **`useArticlePermissions` composable**: Unit test all role/ownership combinations (admin/editor/contributor × own/others articles). This is the deep module that encapsulates permission logic.
- **AdminArticlesView**: Test that action buttons render correctly for each role. Test that contributors see "View Only" on non-owned articles.
- **AdminArticleEditView**: Test that contributors are redirected when trying to edit non-owned articles. Test that publish toggle is hidden for contributors.
- **Prior art**: Existing frontend tests in `frontend/src/views/__tests__/` and `frontend/src/composables/__tests__/` use Vitest + `@vue/test-utils`.

## Out of Scope

- Backend permission changes (already correct)
- Article list filtering (contributors still see all articles)
- Role-based API response filtering (backend returns all articles to all authenticated users)
- "Change Author" dropdown visibility (already admin-only, no changes needed)
- Revision panel visibility for contributors (already works correctly)

## Further Notes

- The `PERMISSIONS` dict in `permission_service.py` is the single source of truth. If permissions change in the future, the frontend composable will need to be updated to match.
- The `useArticlePermissions` composable should be placed in `frontend/src/composables/useArticlePermissions.ts` alongside other composables.
- Consider future extraction of a `RoleGuard` component for reusable permission-based UI gating.
