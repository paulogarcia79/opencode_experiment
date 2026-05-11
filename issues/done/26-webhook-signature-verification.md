## Parent

PRD: Bounce Handling (prd/PRD-bounce-handling.md)

## What to build

Add Svix signature verification to the webhook endpoint to prevent forged requests. Add `RESEND_WEBHOOK_SECRET` environment variable. Use the `svix` Python SDK to verify `Svix-Id`, `Svix-Timestamp`, and `Svix-Signature` headers. Reject invalid or missing signatures with 401. If the secret is not configured, log a warning but continue processing (for local development).

## Acceptance criteria

- [ ] `svix` package added to `pyproject.toml`
- [ ] `RESEND_WEBHOOK_SECRET` added to `app/config.py` and `.env.example`
- [ ] Webhook endpoint verifies Svix signature when secret is configured
- [ ] Invalid signature → 401
- [ ] Missing signature (when secret configured) → 401
- [ ] No secret configured → warning log, events processed (dev mode)
- [ ] Test: valid signature passes
- [ ] Test: invalid signature rejected
- [ ] `just test` passes

## Blocked by

- None - can start immediately (independent of #25)
