## Parent

PRD: Preview Email (prd/PRD-preview-email.md)

## What to build

End-to-End "Send Preview" Feature. Add a backend endpoint `POST /api/admin/articles/{id}/preview-email` that reuses `send_newsletter_email` with a dummy unsubscribe token and sends to `settings.ADMIN_EMAIL`. Add `sendPreviewEmail` to `useAdminApi.ts`. Add a "Send Preview" button on `AdminArticleEditView.vue` with loading, success, and error states. Include backend tests using `TestClient` and frontend tests for the button interactions and state updates.

## Acceptance criteria

- [ ] Backend `POST /api/admin/articles/{id}/preview-email` endpoint implemented and secured.
- [ ] Endpoint sends to `settings.ADMIN_EMAIL` using `send_newsletter_email`.
- [ ] Frontend `sendPreviewEmail` added to `useAdminApi.ts`.
- [ ] "Send Preview" button added to `AdminArticleEditView.vue` (only shown if article is saved/has an ID).
- [ ] UI shows loading, success, and error states when preview is sent.
- [ ] Backend tests written.
- [ ] Frontend tests written.

## Blocked by

None - can start immediately
