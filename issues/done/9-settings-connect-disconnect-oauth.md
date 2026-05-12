## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Implement connect/disconnect OAuth providers from the settings page. Includes backend endpoints and frontend interactions, with protection against disconnecting the only login method.

## Acceptance criteria

- [ ] `POST /api/admin/settings/accounts/oauth/{provider}` initiates OAuth connection, redirects to provider
- [ ] `DELETE /api/admin/settings/accounts/oauth/{provider}` removes UserOAuthProvider record
- [ ] Disconnect returns 400 with error message if it's the only login method (no password set AND no other OAuth providers)
- [ ] OAuth callback for connection flow redirects back to `/admin/settings` (not `/admin`)
- [ ] Settings page shows loading state during connect/disconnect
- [ ] Settings page shows error toast/message when disconnect is blocked
- [ ] Vitest tests for connect/disconnect interactions and error display
- [ ] Backend tests for disconnect protection logic

## Blocked by

- #7 (oauth-service-github)
- #8 (settings-connected-accounts-display)
