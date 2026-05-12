## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Modify the OAuth callback flow to handle new unverified users correctly. When a new user signs in via OAuth and is not yet verified, the callback should redirect them to the verification page instead of issuing a JWT.

## Acceptance criteria

- [ ] OAuth callback detects newly created users (is_verified=False)
- [ ] Newly created users are redirected to `{APP_BASE_URL}/admin/verify-email?email={email}`
- [ ] Existing verified users continue to receive JWT redirect as before
- [ ] Verification email is sent automatically during OAuth callback for new users
- [ ] Tests for both paths (verified redirect vs verification redirect)

## Blocked by

- #3 (oauth-router-google-flow)
- #4 (email-verification-service)
