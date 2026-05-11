## Parent

PRD: Bounce Handling (prd/PRD-bounce-handling.md)

## What to build

Handle `email.bounced` webhook events. When a permanent bounce is detected (`data.bounce.type == "Permanent"`), look up the subscriber by email and set `status = "unsubscribed"`. Update the corresponding `NewsletterSend` record with `status = "failed"` and include bounce details in `error_message`. Transient bounces only update `NewsletterSend` — subscriber status remains unchanged.

## Acceptance criteria

- [ ] `email.bounced` event handler checks `data.bounce.type`
- [ ] Permanent bounce → subscriber `status = "unsubscribed"`, `NewsletterSend` updated with bounce details
- [ ] Transient bounce → subscriber status unchanged, `NewsletterSend` updated
- [ ] Test: permanent bounce unsubscribes subscriber
- [ ] Test: transient bounce does NOT unsubscribe subscriber
- [ ] Test: bounce details stored in `error_message`
- [ ] `just test` passes

## Blocked by

- #25-webhook-idempotency.md
- #26-webhook-signature-verification.md
