## Parent

PRD: `prd/PRD-role-based-dashboards.md`

## What to build

Restructure the Vue Router with three separate namespace trees (`/admin/*`, `/editor/*`, `/contributor/*`), create the shared `DashboardLayout` base component with a nav slot, build the three thin role-specific wrappers (`AdminDashboard`, `EditorDashboard`, `ContributorDashboard`), implement role-based route guards, add login redirect by role, and create the `/forbidden` page. Write Vitest tests for routing and layout behavior.

**End-to-end behavior**: A user logs in → redirected to their role's dashboard. An editor visiting `/admin` → redirected to `/forbidden` with a link back to `/editor`. Each dashboard shows the correct nav items for its role.

## Acceptance criteria

- [ ] Router: three route trees under `/admin`, `/editor`, `/contributor`
- [ ] `DashboardLayout.vue`: base component with sticky top nav bar, `<slot name="nav-items">`, `<slot name="content">`, logout button
- [ ] `AdminDashboard.vue`: nav items = Articles, Import, Media, Tags, Analytics, Settings, Users (plus Review tab with badge from API)
- [ ] `EditorDashboard.vue`: nav items = Articles, Review (with badge), Import, Settings
- [ ] `ContributorDashboard.vue`: nav items = Articles, Import, Settings
- [ ] Route guards in `beforeEach`: `/admin/*` requires `role === 'admin'`; `/editor/*` requires `admin` or `editor`; `/contributor/*` requires any authenticated user. Violations redirect to `/forbidden`
- [ ] Cross-namespace editor redirect: editor visiting `/contributor/articles/:id/edit` redirects to `/editor/articles/:id/edit`
- [ ] Login page: after successful login + `/api/auth/me`, redirect to dashboard based on `user.role`
- [ ] Login redirect persists across existing router guard (no double-redirect issues)
- [ ] `/forbidden` route: shows "403 — You don't have access" with link back to user's own dashboard (computed from store role)
- [ ] `/admin/login` path preserved as the single login page
- [ ] Frontend tests (Vitest): nav items per role, route guards redirect correctly, forbidden page dashboard link per role, login redirect behavior, cross-namespace editor redirect

## Blocked by

- Issue 1 (Backend: Models, permissions, and API hardening)
