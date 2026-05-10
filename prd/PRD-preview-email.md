## Problem Statement

Admins currently have no way to verify how an article's rendered HTML will look in an actual email client before sending the newsletter to the entire subscriber list. Hitting "Publish and Send" immediately blasts the email out to all active subscribers, leaving no room for manual QA of image rendering, typography, or link correctness. This creates anxiety around the publishing workflow and increases the risk of sending broken formatting to readers.

## Solution

Add a "Send Preview" feature to the Admin Article Edit view. This allows admins to dispatch a test newsletter email to their own configured admin email address. The preview utilizes the exact same TipTap-to-HTML rendering logic as the production newsletter, ensuring an accurate representation of the final email in a real inbox.

## User Stories

1. As an admin, I want to send a preview of a saved draft article to my email, so that I can verify formatting and image rendering before publishing.
2. As a content creator, I want the preview email to use the exact same HTML rendering logic as the production newsletter, so that my preview is an 100% accurate representation of the final send.
3. As an admin, I want a "Send Preview" button clearly visible in the article edit interface alongside the publish settings, so that testing is a frictionless part of my publishing workflow.
4. As an admin, I want to see loading states and success/error feedback when requesting a preview, so that I know the email was dispatched successfully.
5. As a developer, I want the preview endpoint to reuse the existing `send_newsletter_email` service, so that email formatting logic is not duplicated.
6. As a developer, I want the preview endpoint to be protected by admin authentication, so that unauthorized users cannot trigger arbitrary emails.
7. As a developer, I want the preview feature to operate on a saved article ID rather than raw unsaved JSON, so that the payload is simple and secure.

## Implementation Decisions

- **Modules Built/Modified:**
  - **Backend API:** Add a new `POST /api/admin/articles/{id}/preview-email` endpoint (likely in `app/routers/articles.py`).
  - **Frontend API Composable:** Add `sendPreviewEmail(id: string)` to `frontend/src/composables/useAdminApi.ts`.
  - **Frontend Edit View:** Add a "Send Preview" button in the settings/actions area of `frontend/src/views/AdminArticleEditView.vue`.
- **Architectural Decisions:**
  - The endpoint operates exclusively on a saved article ID. Admins must rely on auto-save or manual save before previewing the latest changes.
  - The preview email will be dispatched directly to the email address defined in `settings.ADMIN_EMAIL`.
  - Because the admin receiving the preview is not an actual `Subscriber` record, a dummy/placeholder unsubscribe token (e.g., `"preview-mode-no-unsubscribe"`) will be passed to `send_newsletter_email`.
- **API Contracts:**
  - `POST /api/admin/articles/{id}/preview-email`
  - Requires valid JWT via `require_admin`.
  - Returns `200 OK` with a success message (e.g., `{"message": "Preview sent successfully"}`) on successful dispatch.
- **Interactions:**
  - Clicking "Send Preview" will disable the button and show a spinner. On completion, a success/error message will be displayed below or adjacent to the button.

## Testing Decisions

- **What makes a good test:** Verify external behavior. For the backend, ensure the endpoint fetches the correct article, calls the HTML renderer, and invokes the email sending service with the admin's email. For the frontend, verify the button triggers the API call and accurately displays loading/success/error states.
- **Modules to be tested:**
  - `tests/test_articles.py` (or `test_newsletter.py`): Mock the Resend API or `send_newsletter_email` function. Assert that calling the preview endpoint triggers the mock with `settings.ADMIN_EMAIL` and the correct rendered HTML.
  - `frontend/src/views/__tests__/AdminArticleEditView.spec.ts`: Mock `sendPreviewEmail`. Assert that clicking the preview button calls the mock with the correct article ID and that UI states update accordingly.
- **Prior art:** Existing backend tests use `TestClient` and `unittest.mock.patch` to verify email dispatches without hitting the actual Resend API. Frontend tests use `@vue/test-utils` and `flushPromises` to test async button interactions.

## Out of Scope

- **Unsaved Content Preview:** Passing raw, unsaved TipTap JSON payloads to the endpoint.
- **Custom Email Targets:** Allowing the admin to type in an arbitrary email address to send the preview to (restricted to `ADMIN_EMAIL` only).
- **In-App HTML Preview:** Rendering the HTML preview within an iframe or modal in the UI. We are prioritizing actual email delivery for the most accurate test.

## Further Notes

- The feature relies on the `RESEND_API_KEY` being properly configured. If the key is missing, `send_newsletter_email` currently exits early. The preview endpoint should probably surface this limitation gracefully if the email is not actually sent.
