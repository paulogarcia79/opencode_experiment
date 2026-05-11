## Parent

PRD: Password Reset Flow (prd/PRD-password-reset.md)

## What to build

Implement the `POST /api/auth/forgot-password` endpoint that accepts an email, generates a reset token, sends the reset email, and enforces a 60-second per-email cooldown. The endpoint returns the same response regardless of whether the email exists to prevent email enumeration.

## Acceptance criteria

- [x] `ForgotPasswordRequest` schema added to `app/schemas.py` with `email` field
- [x] `POST /api/auth/forgot-password` endpoint accepts `{ "email": "..." }`
- [x] For existing email: generates reset token, sends email via EmailService, returns 200
- [x] For non-existent email: returns identical 200 response (no enumeration)
- [x] In-memory per-email cooldown (60 seconds) — returns 429 if requested too soon
- [x] Response body: `{ "message": "If an account exists with that email, a reset link has been sent" }`
- [x] Test: successful forgot-password request → 200
- [x] Test: non-existent email → 200, same response
- [x] Test: cooldown enforcement → 429 after rapid requests for same email
- [x] `just test` passes

## Blocked by

- #19-reset-token-service-and-tests.md
- #20-reset-email-template.md
