## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Build the three verification UI components that together create the graduated unverified-user experience. (1) **VerificationBanner**: a global component rendered in `App.vue` below the header. Visible when the user is authenticated and `is_verified === false`. Shows "Verify your email to unlock full access." with a "Resend verification" button. Dismissible — dismissal stored in the session-level `isVerificationBannerDismissed` ref (clears on page refresh). Relies on the global 403 `EMAIL_NOT_VERIFIED` interceptor for visibility (or directly from `store.user.is_verified`). (2) **VerifyEmailView**: a public page at `/verify-email`. Reads `route.query.token`, calls `POST /api/auth/verify-email` with the token. On success: shows success message, auto-redirects to `/` after a short delay. On expired/invalid: shows error message with a link to `/auth?tab=verify&expired=true`. (3) **Dashboard verification prompt**: inside each dashboard shell (`ContributorDashboard`, `EditorDashboard`, `AdminDashboard`), when `store.user?.is_verified === false`, the `<RouterView>` child content slot is replaced with a full-page centered prompt: "Verify your email to access your dashboard" with a "Resend verification" button. When verified, normal dashboard content renders. The resend button calls the bearer-token `resendVerification()` function.

## Acceptance criteria

### VerificationBanner
- [ ] Renders when `store.token` exists and `store.user?.is_verified === false`
- [ ] Also activates when global interceptor sets `verificationRequired`
- [ ] Shows "Verify your email to unlock full access." text
- [ ] "Resend verification" button calls bearer-token `resendVerification()`
- [ ] Dismiss button hides banner for current session (not persisted to localStorage)
- [ ] Banner does not render when user is verified or logged out
- [ ] Banner re-appears after page refresh if still unverified (session-only dismissal)
- [ ] Banner positioned below `SiteHeader`, above `<RouterView>`

### VerifyEmailView
- [ ] Route `/verify-email` (public) renders `VerifyEmailView`
- [ ] Reads `route.query.token` from URL
- [ ] Calls `POST /api/auth/verify-email` with `{"token": "..."}` in request body
- [ ] Success state: shows "Email verified!" message, auto-redirects to `/` after ~2 seconds
- [ ] Error state (invalid/expired token): shows error message
- [ ] Error state: includes link to `/auth?tab=verify&expired=true`
- [ ] Loading state: shows spinner while API call is in flight

### Dashboard verification prompt
- [ ] Renders in `ContributorDashboard`, `EditorDashboard`, `AdminDashboard` when `store.user?.is_verified === false`
- [ ] Prompt replaces entire `<slot />` / `<RouterView />` content area
- [ ] Prompt is centered vertically and horizontally in the content area
- [ ] Shows "Verify your email to access your dashboard" heading
- [ ] "Resend verification" button visible
- [ ] When `is_verified === true`, normal `<RouterView>` child content renders
- [ ] No child route component mounts while prompt is shown

### Tests
- [ ] Frontend tests: banner renders when unverified, hides when verified
- [ ] Frontend tests: banner dismiss persists for session only
- [ ] Frontend tests: banner resend button triggers API call
- [ ] Frontend tests: VerifyEmailView success state with redirect
- [ ] Frontend tests: VerifyEmailView error state with expired link
- [ ] Frontend tests: dashboard prompt renders when unverified
- [ ] Frontend tests: dashboard prompt hidden when verified
- [ ] Frontend tests: dashboard prompt resend button functional
- [ ] `npm run build` passes

## Blocked by

- #55 (route `/verify-email` must exist, dashboard routes must allow unverified)
- #56 (store must have `isVerified`, `isVerificationBannerDismissed`, resend function)
- #58 (SiteHeader renders above banner in App.vue, but banner component is independent)
