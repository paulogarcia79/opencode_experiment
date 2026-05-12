## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Create the admin settings page that displays connected OAuth accounts. Add a Settings link to the admin navigation.

## Acceptance criteria

- [ ] `GET /api/admin/settings/accounts` returns `{email, is_verified, connected_providers: [{provider, connected_at}]}`
- [ ] `AdminSettingsView.vue` at `/admin/settings` displays user email and connected providers
- [ ] Each connected provider shows its name and a "Disconnect" button
- [ ] Unconnected providers show a "Connect" button
- [ ] Settings link added to AdminLayout navigation
- [ ] Router has `/admin/settings` route under admin layout (requires auth)
- [ ] `useAdminApi.ts` has `fetchConnectedAccounts()` function
- [ ] Vitest tests for AdminSettingsView display

## Blocked by

- #1 (database-verification-oauth-models)
