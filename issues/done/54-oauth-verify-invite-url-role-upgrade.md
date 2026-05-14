## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Three small backend changes that complete the auth scope. (1) OAuth account creation (Google, GitHub) sets `is_verified=True` immediately — no verification email is sent for OAuth-registered users. (2) Update the invite email setup URL from `{APP_BASE_URL}/admin/setup?token=xxx` to `{APP_BASE_URL}/auth?setup=xxx` in `send_invite_email()`. (3) When a self-registered contributor completes an admin invite setup, `complete_setup()` overwrites their role to the invited role (e.g., contributor → editor).

## Acceptance criteria

- [ ] OAuth-created users (`handle_oauth_user` or equivalent) get `is_verified=True`
- [ ] OAuth-created users do NOT receive a verification email
- [ ] Existing pre-change OAuth users (already `is_verified=False`) are unaffected
- [ ] `send_invite_email()` generates setup URL as `{APP_BASE_URL}/auth?setup=TOKEN`
- [ ] `complete_setup()` sets user's role to `invite_role` (overwriting existing role)
- [ ] Backend tests: verify OAuth-created user has `is_verified=True`
- [ ] Backend tests: verify invite email contains `/auth?setup=...` URL format
- [ ] Backend tests: verify contributor's role updates to invited role after `complete_setup()`

## Blocked by

None — can start immediately.
