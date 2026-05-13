## Problem Statement

Several bugs and missing features were discovered after implementing role-based dashboards:

1. **Auto-save fires on entering edit mode**: Opening an existing article in the editor triggers auto-save within 2 seconds, which reverts the article status to "draft" — even if the user made no changes. This causes published articles to silently become drafts and pending_review articles to disappear from the review queue.
2. **Contributor redirected when editing own article**: The admin article detail endpoint doesn't return author information, so the ownership check in the editor fails and sends the contributor back to their dashboard.
3. **Contributor cards lack a "Read" button**: Contributors have no way to preview their own articles (drafts, pending_review, or rejected) outside the editor.
4. **Users can edit articles they don't own**: Admin and editor roles can open and modify any article, which contradicts the intended workflow where only authors edit their own content.
5. **Contributor sees unnecessary buttons**: "Update Article" and "Send Preview" buttons are visible to contributors, even though their articles depend on editorial approval.
6. **Review queue badge doesn't update**: After approving or rejecting an article in the review queue, the pending count badge in the navigation bar stays stale until the page is refreshed.

## Solution

Fix the six issues with targeted changes across the auto-save system, article editor, article detail API, contributor dashboard, and review queue. Introduce a read-only editor mode and an article preview view for contributors. Make review queue actions update the navigation badge in real time.

## User Stories

### Auto-Save Fix
1. As any user, I want auto-save to only trigger when I actually make edits, so that opening an article in the editor does not change its status
2. As an editor, I want to open a published article in the editor without it being reverted to draft, so that I can review content safely
3. As an editor, I want to open a pending_review article from the review queue in the full editor without it being removed from the queue, so that I can do a thorough review before deciding

### Article Detail API Fix
4. As a contributor, I want to open my own article in the editor without being redirected to the dashboard, so that I can edit my drafts

### Contributor "Read" Button
5. As a contributor, I want a "Read" button on each article card, so that I can preview my article content without entering the editor
6. As a contributor, I want the preview to render my TipTap content as readable HTML, so that I can see what the final article will look like
7. As a contributor, I want the preview to work regardless of article status (draft, pending_review, published, rejected), so that I can review all my articles

### Read-Only Editor Mode
8. As an editor, I want the article editor to be read-only when I open an article I did not create, so that I can review content but cannot accidentally modify it
9. As an admin, I want all inputs disabled and action buttons hidden when viewing non-owned articles, so that the UI clearly communicates I cannot edit

### Contributor Button Cleanup
10. As a contributor, I should not see the "Update Article" button for existing articles, so that I rely on "Submit for Review" as the only save action
11. As a contributor, I should not see the "Send Preview" button, so that my editor is focused on the review submission workflow

### Review Queue Badge Update
12. As an editor, I want the review queue badge count in the navigation to update after I approve or reject an article, so that I know the current pending count without refreshing

## Implementation Decisions

### Auto-Save — `formTouched` Flag
- The `useAutoSave` composable gains a `formTouched` ref (default `false`).
- The `watch` on `form.value` only calls `doSave()` when `formTouched === true`.
- The composable exposes a `markFormTouched()` function that the editor calls when the user actually interacts (keyboard input, content change, title change).
- When `onMounted` populates the form from a loaded article, `formTouched` remains `false`, so no auto-save triggers.
- No backend change needed — the root cause is purely in the frontend trigger.

### Article Detail Endpoint — Author Eager-Load
- `GET /api/admin/articles/{id}` adds `selectinload(Article.author)` to the query.
- The response manually includes `author: { id, email }` dict, matching the pattern used by other endpoints (list, review queue).
- This fixes the contributor redirect bug where `article.author?.id` was `undefined`.

### Read-Only Editor Mode
- `AdminArticleEditView.vue` gains a `isReadOnly` computed: `true` when the article author does not match the current user.
- In read-only mode: all text inputs are `disabled`, the TipTap editor is set to `editable: false`, action buttons are hidden.
- Admin/editor can still view any article's content; they just cannot edit it.
- The "Change Author" dropdown (admin-only) remains visible even in read-only mode.

### Article Preview View
- New route: `/contributor/articles/:id/preview`.
- New component: `ArticlePreviewView.vue`.
- Fetches the article via `GET /api/admin/articles/{id}`, renders `content` (TipTap JSON) to HTML using the `@tiptap/html` package.
- Styled to match the public article page (same fonts, spacing, dark aesthetic).
- Includes a "Back to Dashboard" link at the top.
- Accessible regardless of article status (draft, pending_review, published, rejected).

### Contributor Cards — "Read" Button
- `ContributorCardsView.vue` gains a "Read" button on each card.
- Links to `/contributor/articles/{id}/preview`.
- Uses a neutral style (distinct from Edit/Delete) — e.g., a subtle outline button.

### Contributor Button Cleanup
- In `AdminArticleEditView.vue`, the main submit button ("Update Article") is hidden for contributors. New articles still show "Create Article".
- The "Send Preview" button is hidden for contributors at all times.
- Only the review-action button (Submit/Update/Re-submit for Review) remains as the contributor's submit action.

### Review Queue Badge Update
- `ReviewQueue.vue` emits a `count-updated` event after successful approve/reject.
- `AdminDashboard.vue` and `EditorDashboard.vue` listen for this event and re-fetch `GET /api/admin/articles/review/count`, updating their `pendingCount` ref.
- The event bubbles up via the component tree (ReviewQueue → DashboardLayout → Dashboard wrappers).

## Testing Decisions

### What Makes a Good Test
- Backend: test API responses and status codes — verify the detail endpoint now returns author info.
- Frontend: test component rendering with mocked stores/stubs — verify read-only mode disables inputs, verify auto-save doesn't fire on mount, verify "Read" button renders and links correctly.

### Backend Tests (pytest)
- Article detail endpoint now includes author info in response
- Article detail endpoint still returns 404 for contributor on non-owned article

### Frontend Tests (Vitest)
- `useAutoSave`: `formTouched` flag — auto-save does NOT fire when `formTouched` is false; does fire when true
- `AdminArticleEditView`: read-only mode disables inputs and hides action buttons for non-owner; contributor sees no "Update Article" or "Send Preview" buttons
- `ContributorCardsView`: "Read" button renders and links to the correct preview URL
- `ReviewQueue`: approve/reject fires `count-updated` event

### Prior Art
- Backend tests follow pattern from `tests/` directory using FastAPI `TestClient` and SQLite in-memory
- Frontend tests follow pattern from `frontend/src/views/__tests__/` and `frontend/src/composables/__tests__/`
- Existing `useAutoSave.spec.ts` and `AdminArticleEditView.spec.ts` serve as reference for auto-save and editor tests

## Out of Scope

- Changing the backend autosave endpoint status behavior (the frontend `formTouched` flag is sufficient)
- Backend enforcement of read-only mode (the frontend simply doesn't call save/update for non-owned articles)
- Preview for non-contributor roles (editors/admins use the editor for review)
- Changing the "Change Author" dropdown visibility in read-only mode
- Email notifications for review actions

## Further Notes

- The `formTouched` flag approach is safer than trying to suppress the watch during `onMounted` because it handles all edge cases (data loaded from API, restored from revisions, etc.)
- The preview view reuses the existing `@tiptap/html` package already used in `app/services/tiptap_renderer.py` for email rendering
- The read-only mode still allows admin to use the "Change Author" dropdown — this is intentional since reassignment doesn't modify article content
- The review queue badge update uses a parent-child event emission pattern rather than a global store to keep the implementation simple and scoped
