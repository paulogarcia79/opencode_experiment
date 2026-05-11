## Problem Statement

When newsletter emails bounce (permanently rejected by recipient's mail server) or are marked as spam by recipients, the system does not automatically update subscriber status. This means we continue attempting to send emails to dead addresses, which damages sender reputation and deliverability. Additionally, the webhook endpoint has no signature verification, allowing anyone to forge bounce events and manipulate subscriber data. Duplicate webhook deliveries from Resend's at-least-once delivery model cause double-counting of opens and clicks in analytics.

## Solution

Enhance the existing webhook handler to process bounce and complaint events: permanently bounced subscribers are automatically marked as unsubscribed, complaints trigger the same action. Add Svix signature verification to the webhook endpoint to prevent forged requests. Use the `EmailEvent` table as an idempotency layer to prevent duplicate processing. Surface bounce rate and complaint rate metrics in the analytics dashboard so admins can monitor email deliverability health.

## User Stories

1. As an admin, I want subscribers with permanently bounced email addresses to be automatically unsubscribed, so that I don't waste sends on dead addresses and protect my sender reputation.
2. As an admin, I want subscribers who mark my emails as spam to be automatically unsubscribed, so that I respect their choice and avoid further complaints.
3. As an admin, I want to see bounce rate and complaint rate in my analytics dashboard, so that I can monitor the health of my email deliverability.
4. As an admin, I want transient (soft) bounces to NOT unsubscribe subscribers, so that valid subscribers aren't lost due to temporary mail server issues.
5. As a developer, I want the webhook endpoint to verify Svix signatures, so that forged webhook requests cannot manipulate subscriber data or analytics.
6. As a developer, I want duplicate webhook deliveries to be ignored, so that analytics counts (opens, clicks) are accurate and not inflated by at-least-once delivery.
7. As a developer, I want bounce details (type, subType, message) to be stored on the NewsletterSend record, so that I can debug delivery failures.
8. As an admin, I want to see bounce and complaint counts in the growth time-series chart, so that I can track trends over time.
9. As a developer, I want the webhook handler to process both single events and batch events from Resend, so that the system handles all webhook payload formats correctly.
10. As an admin, I want bounced subscribers to appear as "unsubscribed" in the subscriber list, so that the status accurately reflects their deliverability state.
11. As a developer, I want the Svix event ID to be stored in the EmailEvent table with a unique constraint, so that idempotency is enforced at the database level.
12. As an admin, I want the complaint event to include the complaint details in the error message, so that I can understand why a subscriber marked the email as spam.

## Implementation Decisions

- **EmailEvent schema**: Add `svix_id` (str, unique, nullable) column to the `email_events` table via Alembic migration. Used as idempotency key — duplicate webhook events with the same Svix ID are skipped.

- **Webhook signature verification**: Add Svix header validation (`Svix-Id`, `Svix-Timestamp`, `Svix-Signature`) to the webhook endpoint. Requires new `RESEND_WEBHOOK_SECRET` environment variable. Uses the `svix` Python SDK to verify the signature. Requests with invalid or missing signatures return 401.

- **Bounce handling**: On `email.bounced` event, check `data.bounce.type`. If "Permanent", look up the subscriber by email (from `data.to`) and set `status = "unsubscribed"`. Update the corresponding `NewsletterSend` record: `status = "failed"`, `error_message` includes bounce type and message. Transient bounces only update `NewsletterSend` (no subscriber status change).

- **Complaint handling**: On `email.complained` event, look up the subscriber by email and set `status = "unsubscribed"`. Update `NewsletterSend` with `status = "failed"`, `error_message = "Complained"`.

- **Idempotency**: Before processing any webhook event, check if an `EmailEvent` with the same `svix_id` already exists. If yes, return 200 without processing. If no, create the `EmailEvent` record and process the event. The unique constraint on `svix_id` ensures database-level idempotency.

- **Subscriber lookup**: Use the `data.to` email address from the webhook payload to find the subscriber. The `newsletter_send_id` tag is used for correlating with `NewsletterSend` records, but subscriber lookup requires the email address since bounce/complaint events may arrive after the send record is created.

- **Analytics updates**: Add `total_bounces` (count of `NewsletterSend` with `status = "failed"` and bounce-related error), `total_complaints`, `bounce_rate` (bounces / total_sent * 100), and `complaint_rate` (complaints / total_sent * 100) to the analytics summary. Add `bounces` and `complaints` to the growth time-series, aggregated by date from `NewsletterSend` records.

- **No new Subscriber fields**: Reuse the existing `status = "unsubscribed"` for both voluntary unsubscribes and bounced/complained subscribers. No schema changes to the Subscriber model.

- **Environment configuration**: Add `RESEND_WEBHOOK_SECRET` to `app/config.py` and `.env.example`. If not set, webhook signature verification is skipped (with a warning log) to allow local development without Svix setup.

## Testing Decisions

- **What makes a good test**: Tests should verify the external behavior of the webhook handler — correct subscriber status changes, correct NewsletterSend updates, correct analytics aggregation, and correct HTTP responses. Implementation details (how Svix verification works internally) should not be tested directly; instead, test that valid signatures pass and invalid ones are rejected.

- **Backend modules to test**:
  - **Webhook router** (`tests/test_webhooks.py` or new file):
    - Valid Svix signature → 200, event processed
    - Invalid Svix signature → 401
    - Missing Svix signature → 401 (when secret is configured)
    - Duplicate event (same svix_id) → 200, no duplicate processing
    - Permanent bounce → subscriber unsubscribed, NewsletterSend updated
    - Transient bounce → subscriber status unchanged, NewsletterSend updated
    - Complaint → subscriber unsubscribed, NewsletterSend updated
    - Batch events payload → all events processed correctly
  - **Analytics endpoint** — Test that bounce and complaint metrics appear in the summary and growth time-series.
  - **Idempotency** — Test that sending the same event twice only processes it once.

- **Prior art**: Backend uses FastAPI `TestClient` with SQLite in-memory database (`tests/conftest.py`). See `tests/test_auth.py` for endpoint testing patterns. The existing webhook handler already processes opens/clicks — extend those patterns for bounce/complaint handling.

## Out of Scope

- Adding a new `bounced` status to the Subscriber model (reusing `unsubscribed` for now).
- Distinguishing between voluntary unsubscribes and bounced subscribers in the UI.
- Handling `email.delivery_delayed`, `email.suppressed`, or other non-critical event types.
- Webhook retry logic (Resend handles retries on their side).
- Admin notification on bounce events (e.g., Slack alert).
- Bounce recovery workflow (re-activating a bounced subscriber with a new email).

## Further Notes

- The `svix` Python package needs to be added to `pyproject.toml`.
- The webhook endpoint currently has no authentication. Adding Svix verification is a security improvement that should be deployed alongside the bounce handling changes.
- If `RESEND_WEBHOOK_SECRET` is not configured, the system should log a warning but continue processing events (to avoid breaking existing deployments). This can be tightened in production.
- The `EmailEvent.raw_payload` field already stores the full Resend webhook payload, which includes bounce details. This can be used for debugging without adding dedicated bounce columns.
- Resend's suppression list is separate from our database. When we mark a subscriber as unsubscribed, we should also consider adding them to Resend's suppression list via the API, but this is out of scope for the initial implementation.
