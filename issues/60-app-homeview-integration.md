## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Wire everything together into `App.vue` and clean up `HomeView.vue`. `App.vue` is updated to render: `SiteHeader` (global header), `VerificationBanner` (below header, conditional), `<RouterView />` (page content), and `ToastContainer`. OAuth callback detection moves here: on mount, if `router.currentRoute.value.query.oauth_code` is present, call `exchangeOAuthCode()`, set the token, fetch the user profile, and redirect to the role-specific dashboard. Remove the OAuth callback detection from the old login page. `HomeView.vue` is cleaned up: remove all header markup and logic (moved to `SiteHeader`), remove the "Articles" nav link, keep the hero section and article list intact. Verify that the landing page renders correctly in both logged-in and logged-out states.

## Acceptance criteria

- [ ] `App.vue` renders `SiteHeader` above `<RouterView>`
- [ ] `App.vue` renders `VerificationBanner` between `SiteHeader` and `<RouterView>` (conditional on auth state)
- [ ] `App.vue` renders `ToastContainer` below `<RouterView>`
- [ ] OAuth callback detection: on mount, checks `route.query.oauth_code`
- [ ] OAuth callback: if code present, calls `exchangeOAuthCode()`, sets token, fetches profile, redirects to dashboard
- [ ] OAuth callback detection removed from `AuthView.vue` (the old `AdminLoginView.vue` pattern)
- [ ] `HomeView.vue` header section removed (no `<header>`, no search bar, no nav links)
- [ ] `HomeView.vue` hero section and article list remain unchanged
- [ ] Landing page renders correctly when logged out: header shows "Log in / Sign up"
- [ ] Landing page renders correctly when logged in: header shows user pill, articles load
- [ ] Landing page renders correctly when logged in and unverified: header shows user pill, banner shows below header, articles load
- [ ] Frontend tests: App.vue renders header globally on any route
- [ ] Frontend tests: App.vue detects and processes OAuth code
- [ ] Frontend tests: HomeView header elements are absent
- [ ] Frontend tests: HomeView "Articles" link is absent
- [ ] Frontend tests: HomeView hero and article list still render
- [ ] `npm run build` passes

## Blocked by

- #57 (AuthView must exist for route resolution)
- #58 (SiteHeader component must exist)
- #59 (VerificationBanner component must exist)
