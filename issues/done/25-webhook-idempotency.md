## Parent

PRD: Bounce Handling (prd/PRD-bounce-handling.md)

## What to build

Add idempotency to the webhook handler by storing the Svix event ID in the EmailEvent table. This prevents duplicate processing when Resend delivers the same webhook event multiple times (at-least-once delivery). Add `svix_id` column with unique constraint to `email_events` via Alembic migration. Update the webhook handler to check for existing `svix_id` before processing any event.

## Acceptance criteria

- [ ] Alembic migration adds `svix_id` (str, unique, nullable) to `email_events` table
- [ ] `EmailEvent` model updated with `svix_id` field
- [ ] Webhook handler checks for existing `svix_id` before processing — skips if duplicate
- [ ] Test: duplicate event (same svix_id) → 200, no duplicate processing
- [ ] Test: new event → 200, processed normally
- [ ] `just test` passes

## Blocked by

- None - can start immediately
