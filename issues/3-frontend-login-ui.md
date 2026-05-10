## Parent

PRD: Password-based Login UI (prd/PRD-password-login.md)

## What to build

Update the frontend to use the new password-based login system. Replace the single API token input with an email and password form, and wire it up to the new backend `/api/auth/login` endpoint.

## Acceptance criteria

- [ ] `frontend/src/composables/useAdminApi.ts` updated with `login(email, password)` function
- [ ] `AdminLoginView.vue` refactored to show Email and Password inputs
- [ ] Form submission handles loading state, calls `login` API, and shows clear error messages on failure
- [ ] Upon successful login, the returned JWT is stored using the existing `admin.ts` store and the user is redirected to `/admin`
- [ ] `frontend/src/views/__tests__/AdminLoginView.spec.ts` updated/created to test rendering, successful submission, and error handling
- [ ] `cd frontend && npm run test` passes

## Blocked by

- 2-backend-enforce-jwt.md
