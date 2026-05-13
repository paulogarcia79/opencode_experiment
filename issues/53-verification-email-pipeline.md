## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Update the verification email pipeline end-to-end. Update the `email_verification.mjml` template to include a role-specific welcome message ("You're now a contributor!"). Add a `role` parameter to `send_verification_email()` so the template can render role-aware content. Change the verification link URL from a direct backend API call to a frontend route (`/verify-email?token=xxx`). Repurpose `POST /api/auth/resend-verification` to require a Bearer token — extract the user from the JWT, generate a fresh verification token, and resend the email. Remove the old public version that accepted email in the request body.

## Acceptance criteria

- [ ] `email_verification.mjml` template includes role-specific welcome text (receives `role` in context)
- [ ] `send_verification_email()` accepts optional `role` parameter and passes it to template context
- [ ] Verification link in email points to `{APP_BASE_URL}/verify-email?token=xxx` (frontend route, not backend API)
- [ ] `POST /api/auth/resend-verification` requires `Authorization: Bearer <token>` header
- [ ] Resend endpoint extracts user from JWT, generates new verification token, sends email
- [ ] Old public behavior (email in request body, no auth) is removed
- [ ] 60-second cooldown still enforced on resend (existing in-memory throttle)
- [ ] Backend tests: verify template context receives correct role
- [ ] Backend tests: verify email link format is `/verify-email?token=...`
- [ ] Backend tests: verify bearer-only resend works for authenticated users
- [ ] Backend tests: verify unauthenticated resend requests receive 401

## Blocked by

None — can start immediately. (The template and service function changes are independent of other slices.)
