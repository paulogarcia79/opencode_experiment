## Problem Statement

The blog platform currently has no public-facing authentication on the landing page. Visitors see only articles with no login or sign-up affordance. Registration is admin-invite-only — an admin must manually invite every user, which blocks organic contributor growth. The login page lives at `/admin/login`, which is misleading since most users are contributors, not admins. There is no public self-service path to becoming a contributor.

Once registered (or OAuth-created), unverified users are hard-blocked from all authenticated endpoints with a generic 401, making it impossible to provide a graceful "verify your email" experience. The frontend cannot distinguish "email not verified" from "bad token," so no meaningful guidance can be shown.

## Solution

A public self-registration flow allows anyone to create a contributor account with email and password (or OAuth). The landing page header becomes auth-aware: showing a "Log in / Sign up" button for visitors, and a user identity pill with dashboard navigation for logged-in users.

Verification becomes a graduated experience: unverified users are auto-logged in after registration, see a dismissible banner on the landing page, and can navigate to their dashboard shell where a full-page prompt guides them to verify. Backend endpoints return a distinct `EMAIL_NOT_VERIFIED` error code so the frontend can surface clear messaging instead of generic 401s. OAuth accounts are auto-verified since the provider already confirmed the email.

The login route is renamed from `/admin/login` to `/auth` and becomes a tabbed hub hosting login, registration, setup (for admin invites), and expired verification. All existing auth routes (`/admin/forgot-password`, `/admin/reset-password`) move under the `/auth` namespace. The header component is extracted from the home page and elevated to a global shell in `App.vue`, shared across all pages.

## User Stories

### Landing Page Header
1. As an unauthenticated visitor, I want to see a "Log in / Sign up" button in the header, so that I can reach the auth page quickly
2. As an unauthenticated visitor, I want to see the public article list and hero section unchanged, so that I can continue browsing content
3. As a logged-in user, I want to see my identity (email) in a user pill in the header, so that I know I'm logged in
4. As a logged-in user, I want a dropdown menu with Dashboard, Settings, and Log out, so that I can navigate my account
5. As a logged-in user, I want the "Dashboard" link to go to my role-specific dashboard, so that I land in the right namespace
6. As any user on mobile, I want a hamburger menu containing search and auth controls, so that I can use all features on a small screen

### Registration
7. As a new user, I want to register with my email, password, and password confirmation, so that I can create a contributor account
8. As a new user, I want real-time password validation (8+ characters, uppercase, lowercase, digit), so that I know my password meets requirements before submitting
9. As a new user, I want to register via Google or GitHub OAuth, so that I can sign up without creating a password
10. As a new user, I want to be automatically logged in after registration, so that I don't need to enter credentials twice
11. As a new user, I want to see a welcome toast on the landing page right after registration, so that I know my account was created
12. As a user who accidentally registers with an already-registered email, I want a "Log in instead" suggestion to appear, so that I can recover without confusion
13. As a user already logged in, I want to be rejected from the registration form with a clear message, so that I don't create duplicate accounts
14. As a newly registered user, I want my role to be "contributor" by default, so that I can start writing articles

### Email Verification
15. As a newly registered user, I want to receive a verification email that welcomes me by role ("You're now a contributor!"), so that I understand my account context
16. As an unverified user on the landing page, I want a persistent dismissible banner saying "Verify your email to unlock full access," so that I see the reminder wherever I browse
17. As an unverified user, I want the verification banner dismissal to last only for the current session, so that I'm reminded again on my next visit
18. As an unverified user, I want to resend my verification email with one click from the banner, so that I can recover from lost emails
19. As an unverified user, I want to click the verification link in my email and be taken to a page that verifies my account, so that I complete the process
20. As a user with an expired verification link, I want to see an expired-link view with a resend option on `/auth`, so that I can get a fresh link
21. As a newly verified user, I want to be redirected to the landing page where the verification banner is gone and my dashboard is unlocked, so that I can start contributing immediately
22. As a user who registered via OAuth, I want my account to be verified immediately, so that I don't need to check my email

### Unverified Dashboard Experience
23. As an unverified user, I want to navigate to my dashboard and see the shell (navigation sidebar/header), so that I can see where I'll work
24. As an unverified user inside the dashboard, I want a full-page "Verify your email to access your dashboard" prompt with a resend button, so that I know exactly what's needed
25. As an unverified user, I want API calls to return a distinct "email not verified" error, so that the frontend can show clear messaging instead of a generic authentication failure

### Auth Hub Page
26. As an unauthenticated user, I want a single `/auth` page with login and register tabs, so that I don't need to find separate pages
27. As a returning user, I want the login tab to be the default view on `/auth`, so that I can sign in quickly
28. As a user on the register tab, I want to see OAuth buttons (Google, GitHub) alongside the email form, so that I can choose my preferred registration method
29. As a user completing an admin invite, I want to set my password via a Setup tab on `/auth`, so that I can activate my account in one place
30. As a logged-in unverified user visiting `/auth`, I want to be redirected to the landing page, so that I see the verification banner there
31. As a logged-in verified user visiting `/auth`, I want to be redirected to my role's dashboard, so that I don't see the login form unnecessarily

### OAuth Authentication
32. As a user completing OAuth login or registration, I want to land back on the landing page and have the OAuth code exchanged automatically, so that the flow is seamless
33. As an OAuth-registered user, I want to be auto-verified and redirected to my dashboard, so that I can start immediately

### Forgot & Reset Password
34. As a user who forgot my password, I can still access the forgot-password flow at `/auth/forgot-password`, so that the flow remains available
35. As a user resetting my password, I can still access the reset-password flow at `/auth/reset-password`, so that I can complete the reset

### Logout
36. As a logged-in user, I want to log out via the header dropdown and be redirected to the landing page, so that I can browse publicly

### Role Upgrades via Invite
37. As a self-registered contributor who later receives an admin invite to become an editor, I want my role to update to the invited role upon completing the invite setup, so that I gain editor permissions

### Backend Authorization
38. As an unverified user, I want the `GET /api/auth/me` endpoint to work so the frontend can read my verification state, so that the UI can adapt
39. As an unverified user, I want the settings accounts endpoint to work so I can view my connected OAuth providers, so that account management remains accessible
40. As an unverified user, I want all other authenticated endpoints to return a 403 with code `EMAIL_NOT_VERIFIED`, so that the frontend can show the verification prompt
41. As a verified user, I want all existing role-based access controls to remain unchanged, so that no permissions are accidentally loosened

### Registration API
42. As a backend operator, I want a 60-second IP-based cooldown on the registration endpoint, so that the endpoint is protected from abuse
43. As a backend operator, I want duplicate email registrations to return a silent success (no token), so that email enumeration is prevented
44. As a backend operator, I want password complexity enforced server-side as a backstop, so that weak passwords are never accepted

## Implementation Decisions

### Architecture
- The `/auth` route replaces `/admin/login` as the single auth hub. No redirect from the old path — all references updated atomically
- The header component is extracted from the home page and elevated to a global shell rendered by `App.vue`, shared across all pages
- OAuth callback detection moves from `AdminLoginView.onMounted` to `App.vue.onMounted`, since the callback always lands on `/`
- The existing `SetupView.vue` and its setup tab UI are absorbed into `AuthView.vue` as a third tab, triggered by the `?setup=TOKEN` query parameter

### Auth Page — `/auth` and Sub-Routes
- `/auth` — tabbed page: Login (default), Register, Setup (`?setup=TOKEN`), Expired Verification (`?tab=verify&expired=true`)
- `/auth/forgot-password` — existing `ForgotPasswordView`, path updated from `/admin/forgot-password`
- `/auth/reset-password` — existing `ResetPasswordView`, path updated from `/admin/reset-password`
- Login tab is the default; no query-param-driven tab switching for login vs register
- Logged-in unverified users are redirected to `/` (landing page with banner)
- Logged-in verified users are redirected to role-specific dashboard

### Registration Endpoint — `POST /api/auth/register`
- Request body: `email`, `password`, `confirm_password`
- Password complexity enforced: minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 digit
- Validation: frontend real-time with visual feedback, backend final validation as security backstop
- On success (new email): creates User with `role="contributor"`, `is_verified=False`, sends verification email, returns `{"token": "...", "type": "bearer"}` plus `X-Registration-New: true` response header
- On duplicate email: returns 200 with generic success message, no token, no email sent (prevents enumeration)
- Rate limited: 60-second IP cooldown between attempts
- Rejects already-authenticated requests with 400
- The frontend detects missing token in the response to show "Log in instead" suggestion for duplicate emails

### Split Auth Dependency
- A new `require_role_allow_unverified` dependency skips the `is_verified` check, applied to `GET /api/auth/me` and the settings accounts endpoint
- The existing `require_role` dependency returns HTTP 403 with body `{"detail": "Email not verified", "code": "EMAIL_NOT_VERIFIED"}` when a user is authenticated but unverified
- This enables the frontend's global fetch interceptor to distinguish "needs verification" from "bad credentials" or "insufficient role"

### Bearer-Token Resend Verification
- `POST /api/auth/resend-verification` is repurposed to require a Bearer token
- Extracts the user from the JWT, generates a fresh verification token, and sends the verification email
- The old public version (email in body, no auth) is removed
- Resend is triggered from the landing page banner, the dashboard verification prompt, and the expired-verification view

### Email Verification Flow
- Verification link in email points to frontend route `/verify-email?token=xxx`
- A new lightweight `VerifyEmailView` page at `/verify-email` reads the token from the URL query, calls `POST /api/auth/verify-email` with the token in the request body, and shows result
- Success: displays success message and auto-redirects to `/` after a short delay
- Expired/invalid token: shows error with link to `/auth?tab=verify&expired=true`
- The expired-verification mode on `/auth` shows "Link expired" message plus a "Resend verification" button

### Verification Email Template
- Existing `email_verification.mjml` updated to include role-specific welcome text ("You're now a contributor!")
- `send_verification_email()` function updated to accept a `role` parameter for template context
- Verification link URL updated to frontend page format

### OAuth Auto-Verification
- OAuth account creation (Google, GitHub) sets `is_verified=True` immediately
- No verification email is sent for OAuth-registered users
- Existing OAuth users created before this change are unaffected

### Invite Email URL Update
- Setup URL in invite emails updated from `{APP_BASE_URL}/admin/setup?token=xxx` to `{APP_BASE_URL}/auth?setup=xxx`

### Header Component
- Site title/logo on the left, search bar center, auth section right
- "Articles" nav link removed from header
- Logged out: single "Log in / Sign up" button linking to `/auth`
- Logged in: user pill showing email, dropdown with Dashboard (role-resolved path), Settings (role-resolved path), Log out
- Dashboard and Settings links resolve dynamically to the user's role-specific dashboard path
- Mobile: hamburger icon opens a drawer containing search bar, auth button/pill, and navigation
- Auth controls show icon-only on mobile (user or door icon), full text on sm+

### Verification Banner
- Global component rendered in `App.vue` below the header
- Visible when user is authenticated and `is_verified === false`
- Message: "Verify your email to unlock full access." with a "Resend verification" button
- Dismissible: dismissal stored in a session-level reactive ref (clears on page refresh)
- Resend button calls the bearer-token resend verification endpoint via an inline API call

### Dashboard Verification Prompt
- Dashboard components (`ContributorDashboard`, `EditorDashboard`, `AdminDashboard`) check `is_verified` on mount
- When unverified: the `<RouterView>` child content slot is replaced with a full-page centered prompt: "Verify your email to access your dashboard" with a "Resend verification" button
- When verified: normal dashboard content renders
- No child route components mount and no API calls are attempted while the prompt is shown

### Router Guard Updates
- `/auth` replaces `/admin/login` throughout: route definition, route name, guard redirects, component references
- New `/verify-email` route (public) for the frontend verification page
- Already-logged-in check for `/auth`: unverified users redirect to `/`, verified users redirect to role-specific dashboard
- Dashboard routes (`/admin`, `/editor`, `/contributor`): allow unverified users through (no `is_verified` check in guard), so the dashboard verification prompt can render

### API Client & Error Interception
- `useAdminApi.ts`: new `register(email, password, confirmPassword)` function and updated `resendVerification()` (bearer-token)
- Global fetch response interceptor: catches 403 responses with error code `EMAIL_NOT_VERIFIED`, triggers a reactive state that the verification banner watches

### Store Changes
- `isVerificationBannerDismissed` ref (session-only, not persisted)
- Handle `X-Registration-New` response header from registration to trigger a welcome toast

### Role Upgrades via Invite
- When a self-registered contributor completes an admin invite setup, the `complete_setup` function sets the user's role to the invited role (overwriting their contributor role)
- The invite setup flow is unchanged except for the URL

### Route Migration
- `/admin/login` → `/auth` (no redirect from old path)
- `/admin/forgot-password` → `/auth/forgot-password`
- `/admin/reset-password` → `/auth/reset-password`
- `/admin/verify-email` → `/verify-email` (new dedicated route)
- `/admin/setup` → absorbed into `/auth?setup=TOKEN`
- All route names updated accordingly (e.g., `admin-login` → `auth`)
- All internal references updated: router guard redirects, component `RouterLink` targets, email link URLs, logout redirects

## Testing Decisions

### What Makes a Good Test
- Test external behavior: API responses, rendered UI elements per auth state, status codes, error codes — not implementation details like computed properties or internal helper functions
- Backend: test each endpoint with each relevant role and verification state, verifying status codes and error codes
- Frontend: test component rendering with mocked Pinia stores to simulate different auth/role/verification states
- Email integration: test that the correct template context is passed and the correct URL format is generated

### Backend Tests (pytest + SQLite in-memory)
- Registration endpoint: test new user creation, password complexity enforcement, duplicate email silent success, IP cooldown, logged-in rejection, role defaults to contributor, verification email triggered
- Split dependency: test `require_role_allow_unverified` passes for unverified users, test `require_role` returns 403 `EMAIL_NOT_VERIFIED` for unverified users, test both pass for verified users
- Bearer-token resend: test JWT extraction, token regeneration, cooldown enforcement, unauthenticated access returns 401
- OAuth auto-verification: test OAuth-created users have `is_verified=True`, test `is_verified=False` users are NOT verified
- Verification email: test role is passed to template context, test link points to frontend `/verify-email` route
- Invite email: test setup URL format is `/auth?setup=TOKEN`
- Role upgrade on setup: test contributor's role updates to invited role after `complete_setup`

### Frontend Tests (Vitest + @vue/test-utils)
- AuthView: test login tab renders by default, register tab renders with password fields and OAuth buttons, setup tab renders when `?setup=` is present, expired-verify mode renders with resend button
- SiteHeader: test logged-out state shows "Log in / Sign up" button, logged-in state shows user pill with dropdown, logout clears token and redirects to `/`, mobile hamburger toggles drawer
- VerificationBanner: test banner renders when unverified, dismiss hides banner for session, resend button triggers API call, banner does not render when verified or logged out
- VerifyEmailView: test success state on valid token, error state on invalid/expired token, redirect behavior
- Dashboard verification prompt: test prompt renders when unverified, child content hidden, resend button functional, prompt does not render when verified
- Router: test guard redirects (unverified from `/auth` to `/`, verified from `/auth` to dashboard, dashboard routes allowed for unverified)
- App.vue: test header renders globally, OAuth code param triggers exchange
- HomeView: test header elements are absent (moved to App.vue), "Articles" link is absent
- API composable: test register function sends correct payload, handles token response, handles duplicate-email (no token), resend uses bearer token
- Store: test banner dismissal is session-only, `X-Registration-New` header triggers welcome toast

### Prior Art
- Backend tests follow pattern from `tests/` directory using FastAPI `TestClient` and SQLite in-memory databases
- Frontend tests follow pattern from `frontend/src/views/__tests__/` and `frontend/src/composables/__tests__/`
- Existing tests for `useAdminApi`, `admin` store, router guards, and dashboard components serve as direct reference
- PRD-password-reset and PRD-role-based-dashboards tests demonstrate the expected testing patterns

## Out of Scope

- Public-facing user profile pages or avatars
- Contributor-to-editor self-service promotion (admin invite remains the only promotion path)
- Email notifications for review workflow or publishing events
- Two-factor authentication
- CAPTCHA or bot-detection on registration (IP cooldown only)
- Changes to the article review workflow (existing contributor → submit → approve flow unchanged)
- Changes to newsletter subscriptions, email tracking, or email webhook handling
- Tag management, media library, or analytics access changes (existing role permissions unchanged)
- Slug generation changes
- Design system changes (existing dark-tech aesthetic preserved)
- Social sharing or SEO metadata changes
- Password reset flow logic changes (only route path renamed)

## Further Notes

- The "silent success" duplicate email pattern prevents email enumeration: an attacker cannot distinguish "email not registered" from "already registered"
- The `X-Registration-New` header is consumed only by the frontend and is not persisted or exposed
- Session-only banner dismissal uses a Pinia store ref, not `localStorage` — intentional to avoid stale `is_verified` state after verification
- The dashboard full-page prompt replaces the `<RouterView>` slot entirely, so child route components (`onMounted` hooks, API fetches) never execute for unverified users
- The `require_role_allow_unverified` dependency is only used for two endpoints; all other authenticated endpoints use the strict variant
- Setup tab on `/auth` only renders when the `?setup=TOKEN` query parameter is present; it is not discoverable from the tab navigation
- Expired verification mode on `/auth` only renders when `?tab=verify&expired=true` is present; it is not navigable from the tab bar
