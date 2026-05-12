## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Add OAuth login buttons to the admin login page and create the email verification page. The login page should have Google and GitHub buttons below the existing email/password form. The verification page shows a "Check your inbox" message with a resend option.

## Acceptance criteria

- [ ] AdminLoginView has "Sign in with Google" and "Sign in with GitHub" buttons below email/password form
- [ ] Buttons have "or continue with" divider between password form and OAuth buttons
- [ ] Clicking OAuth button redirects browser to `/api/auth/oauth/{provider}`
- [ ] VerifyEmailView at `/admin/verify-email` displays "Check your inbox" message
- [ ] VerifyEmailView shows the email address and has a "Resend verification email" button
- [ ] Resend button calls `POST /api/auth/resend-verification` and shows success/error state
- [ ] `/admin` route handles `?oauth_token=xxx` query param, stores token, redirects to `/admin`
- [ ] Router has `/admin/verify-email` route marked as public
- [ ] Vitest tests for AdminLoginView OAuth buttons and VerifyEmailView

## Blocked by

- #3 (oauth-router-google-flow)
- #5 (oauth-callback-verification-redirect)
