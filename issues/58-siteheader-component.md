## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Extract the header from `HomeView.vue` into a global `SiteHeader.vue` component rendered by `App.vue`. The header shows: site title/logo (left), search bar (center), auth section (right). **Logged out:** single "Log in / Sign up" button linking to `/auth`. **Logged in:** user pill showing the user's email, with a dropdown containing Dashboard (role-resolved path, e.g. `/contributor`), Settings (role-resolved path), and Log out (clears token, redirects to `/`). Dropdown links resolve dynamically based on `store.user.role`. The "Articles" nav link is removed. **Mobile:** hamburger icon opens a drawer containing search bar, auth button/pill, and navigation links. Auth controls show icon-only on mobile (user icon for logged in, door icon for logged out), full text on `sm+`. The existing search bar behavior (`handleSearch` navigating to `/search`) is preserved.

## Acceptance criteria

- [ ] `SiteHeader.vue` component created with site title/logo, search bar, auth section
- [ ] Site title links to `/`
- [ ] Search bar preserves existing behavior (submit → `/search?q=...`)
- [ ] Logged out: "Log in / Sign up" button visible, links to `/auth`
- [ ] Logged in: user pill visible showing email (truncated if long)
- [ ] Logged in: dropdown opens on click, contains Dashboard, Settings, Log out
- [ ] Dashboard link resolves to role-specific path (e.g., `/contributor` for contributor role)
- [ ] Settings link resolves to role-specific path (e.g., `/contributor/settings`)
- [ ] Log out clears token and redirects to `/`
- [ ] "Articles" nav link removed from header
- [ ] Mobile: hamburger icon visible below `sm` breakpoint
- [ ] Mobile: drawer toggles on hamburger click, contains search + auth controls
- [ ] Mobile: auth controls show icon-only (no text) below `sm`
- [ ] Desktop (`sm+`): auth controls show full text
- [ ] `HomeView.vue` header content removed (only the section below header remains)
- [ ] Frontend tests: logged-out header shows "Log in / Sign up" button
- [ ] Frontend tests: logged-in header shows user pill with email
- [ ] Frontend tests: dropdown opens and shows Dashboard, Settings, Log out
- [ ] Frontend tests: Dashboard link resolves to correct role path
- [ ] Frontend tests: logout clears store and triggers redirect to `/`
- [ ] Frontend tests: mobile hamburger toggles drawer
- [ ] `npm run build` passes

## Blocked by

- #55 (route `/auth` must exist for the "Log in / Sign up" link)
- #56 (store must have `user`, `token`, `clearToken` for the auth-aware rendering)
