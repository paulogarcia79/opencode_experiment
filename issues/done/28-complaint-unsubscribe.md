## Parent

PRD: Bounce Handling (prd/PRD-bounce-handling.md)

## What to build

Handle `email.complained` webhook events. When a subscriber marks an email as spam, look up the subscriber by email and set `status = "unsubscribed"`. Update the corresponding `NewsletterSend` record with `status = "failed"` and `error_message = "Complained"`.

## Acceptance criteria

- [ ] `email.complained` event handler implemented
- [ ] Subscriber `status = "unsubscribed"` on complaint
- [ ] `NewsletterSend` updated with `status = "failed"`, `error_message = "Complained"`
- [ ] Test: complaint unsubscribes subscriber
- [ ] Test: complaint updates NewsletterSend
- [ ] `just test` passes

## Blocked by

- #25-webhook-idempotency.md
- #26-webhook-signature-verification.md
