## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Add GitHub as a second OAuth provider. Reuses the OAuth service infrastructure from the Google implementation.

## Acceptance criteria

- [ ] `app/config.py` has `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` settings
- [ ] OAuth service supports `github` provider
- [ ] GitHub uses OAuth2 with scope `user:email`
- [ ] Primary email fetched from `https://api.github.com/user/emails` (filter `primary: true, verified: true`)
- [ ] `GET /api/auth/oauth/github` redirects to GitHub authorization URL
- [ ] `GET /api/auth/oauth/github/callback` exchanges code, creates/links user, redirects to frontend
- [ ] Same auto-link by email and auto-create behavior as Google
- [ ] Tests for GitHub authorization URL, callback, user info extraction

## Blocked by

- #2 (oauth-service-google)
