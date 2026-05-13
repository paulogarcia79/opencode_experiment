## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Migrate all auth-related frontend routes and the navigation guard. Rename `/admin/login` → `/auth` (route name `admin-login` → `auth`), `/admin/forgot-password` → `/auth/forgot-password`, `/admin/reset-password` → `/auth/reset-password`. Add a new public route `/verify-email` for the verification link landing page. Remove the `/admin/setup` route (absorbed into `/auth?setup=TOKEN`, handled in a later slice). Update the router guard: logged-in unverified users visiting `/auth` are redirected to `/`; logged-in verified users visiting `/auth` are redirected to their role-specific dashboard. Dashboard routes (`/admin`, `/editor`, `/contributor`) must allow unverified users through (no `is_verified` guard rejection — the dashboard components themselves will show the verification prompt, handled in another slice). Update all hardcoded route references: logout redirect to `/`, component `RouterLink` targets, route name references in redirect logic.

## Acceptance criteria

- [ ] `/auth` route defined with `meta: { public: true }`, replaces `/admin/login`
- [ ] `/auth/forgot-password` route defined (same component, new path)
- [ ] `/auth/reset-password` route defined (same component, new path)
- [ ] New `/verify-email` route defined with `meta: { public: true }`
- [ ] Old `/admin/setup` route removed
- [ ] Router guard: unverified logged-in user on `/auth` redirects to `/`
- [ ] Router guard: verified logged-in user on `/auth` redirects to role dashboard
- [ ] Router guard: unverified users allowed through to dashboard routes (no `is_verified` rejection)
- [ ] Route name updated: `admin-login` → `auth`, `admin-forgot-password` → `auth-forgot-password`, `admin-reset-password` → `auth-reset-password`, `admin-verify-email` → removed
- [ ] All internal references updated: guard redirects, logout, component `RouterLink` targets, `getDashboardForRole()` references
- [ ] Frontend tests: test guard redirects for each auth/verification state
- [ ] Frontend tests: test dashboard routes allow unverified users
- [ ] Frontend tests: test old routes return no match
- [ ] `npm run build` passes (type-check, no broken imports)

## Blocked by

None — can start immediately. Route definitions and guard logic are frontend-only.
