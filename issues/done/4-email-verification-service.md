## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Implement the email verification service and endpoints. This includes token generation, validation, email sending, and the verification/resend endpoints. The `require_admin` dependency must reject unverified users.

## Acceptance criteria

- [ ] Email verification service generates token, stores hash + 24h expiry on User
- [ ] `POST /api/auth/verify-email` accepts `{token}`, validates, sets `is_verified=True`, returns `{token, type: "bearer"}`
- [ ] `POST /api/auth/resend-verification` accepts `{email}`, sends new verification email, has 60s cooldown per email
- [ ] `app/services/email_service.py` has `send_verification_email(email, token)` function
- [ ] `app/templates/email/email_verification.mjml` template exists with branded design
- [ ] `require_admin` in `app/dependencies.py` rejects users where `is_verified=False` with 401
- [ ] Tests for token generation, validation, expiry, resend cooldown, unverified user rejection

## Blocked by

- #1 (database-verification-oauth-models)
