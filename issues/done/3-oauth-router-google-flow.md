## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Add the OAuth router endpoints for Google login flow. When a user initiates Google OAuth, they are redirected to Google's authorization page. On callback, the system exchanges the code, creates or links the user account, and redirects back to the frontend with a JWT.

## Acceptance criteria

- [ ] `GET /api/auth/oauth/google` redirects to Google authorization URL with state parameter
- [ ] `GET /api/auth/oauth/google/callback` exchanges code for tokens, fetches user info
- [ ] If email matches existing user, auto-links by creating UserOAuthProvider record
- [ ] If no user exists, creates new user with `is_verified=False` and random unusable password
- [ ] On success, redirects to `{APP_BASE_URL}/admin?oauth_token={jwt}` for verified users
- [ ] On success, redirects to `{APP_BASE_URL}/admin/verify-email?email={email}` for unverified new users
- [ ] State parameter validated to prevent CSRF attacks
- [ ] Tests for redirect behavior, callback with existing user (auto-link), callback with new user (create)

## Blocked by

- #2 (oauth-service-google)
