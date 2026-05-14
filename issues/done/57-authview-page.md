## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Build the `AuthView.vue` page at `/auth` — a tabbed hub replacing `AdminLoginView.vue` and absorbing `SetupView.vue`. Four modes: **Login tab** (default) with email/password form and Google/GitHub OAuth buttons. **Register tab** with email, password, confirm password fields, real-time password complexity validation (green/red indicators per rule), and OAuth buttons. **Setup tab** (shown when `?setup=TOKEN` query param is present) with password and confirm password fields, calls `setupAccount()`, on success redirects to `/auth` login tab. **Expired verification mode** (shown when `?tab=verify&expired=true`) with "Link expired" message and resend button. The existing `AdminLoginView.vue` and `SetupView.vue` components are removed or repurposed into this unified component. On successful login or registration, auto-login behavior: registration stays on `/` (handled by the API composable), login redirects to dashboard.

## Acceptance criteria

- [ ] `AuthView.vue` component at `/auth` route
- [ ] Login tab is the default view on page load
- [ ] Login tab: email/password form, OAuth buttons (Google, GitHub), "Forgot password?" link to `/auth/forgot-password`
- [ ] Register tab: email, password, confirm password fields
- [ ] Register tab: real-time password validation with visual feedback (at least 8 chars, has uppercase, has lowercase, has digit)
- [ ] Register tab: "Passwords match" indicator
- [ ] Register tab: OAuth buttons (Google, GitHub)
- [ ] Register tab: on success, calls `register()`, auto-login behavior handled by API composable
- [ ] Register tab: on duplicate email, shows "An account with this email may already exist. Log in instead" with link switching to login tab
- [ ] Setup tab: renders when `route.query.setup` is present
- [ ] Setup tab: password + confirm password fields, calls `setupAccount()`
- [ ] Setup tab: on success, shows success state and redirects to login tab
- [ ] Expired verification mode: renders when `route.query.tab === 'verify' && route.query.expired === 'true'`
- [ ] Expired verification mode: shows "Link expired" message + "Resend verification" button
- [ ] Tab switching: clicking "Register" / "Log in" tab links switches between tabs without query params
- [ ] Old `AdminLoginView.vue` and `SetupView.vue` files removed
- [ ] Frontend tests: login tab renders by default
- [ ] Frontend tests: register tab shows password fields and OAuth buttons
- [ ] Frontend tests: password validation indicators update in real-time
- [ ] Frontend tests: setup tab renders when `?setup=TOKEN` present
- [ ] Frontend tests: expired-verify mode renders with resend button
- [ ] Frontend tests: duplicate email shows "Log in instead" suggestion
- [ ] `npm run build` passes

## Blocked by

- #55 (route `/auth` must exist)
- #56 (store + API composable functions must exist)
