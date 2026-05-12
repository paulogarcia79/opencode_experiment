## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Implement the OAuth service with Google as the first provider. This is a deep module that encapsulates authorization URL generation, token exchange, and user info extraction. Add Google OAuth config variables.

## Acceptance criteria

- [ ] `app/config.py` has `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` settings
- [ ] `app/services/oauth_service.py` exists with `authorize(provider) -> url`, `handle_callback(provider, code, state) -> user_info`, `get_user_email(provider, user_info) -> email`
- [ ] Google provider uses OpenID Connect with scope `openid email profile`
- [ ] User info fetched from `https://openidconnect.googleapis.com/v1/userinfo`
- [ ] `email_verified` claim from Google is captured
- [ ] `authlib` is added to project dependencies
- [ ] Tests for authorization URL generation (correct URL, state parameter, scopes)
- [ ] Tests for user info extraction (email, provider_user_id, email_verified)

## Blocked by

- #1 (database-verification-oauth-models)
