## Parent

[PRD-email-tracking.md](../prd/PRD-email-tracking.md)

## What to build

Update the email service to ensure every newsletter sent is traceable. This involves passing a unique identifier to Resend and enabling their native open/click tracking features via the API.

## Acceptance criteria

- [ ] `app/services/email_service.py` updated to include a `headers` or `tags` parameter in `resend.Emails.send` containing the `NewsletterSend.id`.
- [ ] Resend API calls explicitly enable `open_tracking` and `click_tracking`.
- [ ] Webhook handler updated to match incoming Resend events (via `email_id` or custom ID) back to the corresponding `NewsletterSend` record.
- [ ] Tests verify that receiving a "delivered" or "open" webhook updates the `NewsletterSend` record correctly.

## Blocked by

- [14-tracking-schema-and-webhook-infrastructure.md](./14-tracking-schema-and-webhook-infrastructure.md)
