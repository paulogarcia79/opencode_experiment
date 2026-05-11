## Parent

[PRD-email-tracking.md](../prd/PRD-email-tracking.md)

## What to build

Update the database schema and implement the base webhook endpoint for Resend events. This includes adding engagement tracking fields to `NewsletterSend` and creating the `EmailEvent` model to store raw webhook data.

## Acceptance criteria

- [ ] `NewsletterSend` model updated with `opened_at`, `clicked_at`, `open_count`, and `click_count`.
- [ ] New `EmailEvent` model created to log raw webhook payloads.
- [ ] Database migration generated and applied.
- [ ] Public endpoint `POST /api/webhooks/resend` implemented.
- [ ] Endpoint correctly parses Resend webhook payloads and logs them to the `EmailEvent` table.

## Blocked by

None - can start immediately
