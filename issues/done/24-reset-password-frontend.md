## Parent

PRD: Password Reset Flow (prd/PRD-password-reset.md)

## What to build

Build the Reset Password page in the frontend. This includes the `ResetPasswordView.vue` component with password + confirm password inputs, the `resetPassword()` function in `useAdminApi.ts`, the router route, and Vitest tests. The page reads the token from the URL query param, submits the reset request, and redirects to login on success.

## Acceptance criteria

- [x] `resetPassword(token, newPassword)` function added to `frontend/src/composables/useAdminApi.ts`
- [x] `ResetPasswordView.vue` created with new password + confirm password inputs and submit button
- [x] Reads `token` from `?token=` URL query param on page load
- [x] Form calls `resetPassword` API on submission with token + new password
- [x] Password confirmation validates client-side (passwords must match)
- [x] Shows loading spinner during submission
- [x] Shows error state for invalid/expired token
- [x] On success: redirects to `/admin/login` with success indicator
- [x] Styled consistently with `AdminLoginView.vue` (dark tech aesthetic, Tailwind)
- [x] Router route `/admin/reset-password` added as public route (`meta: { public: true }`)
- [x] `frontend/src/views/__tests__/ResetPasswordView.spec.ts` — tests rendering, token from URL, form submission, password match validation, redirect on success, error for invalid token
- [x] `cd frontend && npm run test` passes
- [x] `cd frontend && npm run build` passes (vue-tsc type-check)

## Blocked by

- #22-reset-password-endpoint.md
- #23-forgot-password-frontend.md
