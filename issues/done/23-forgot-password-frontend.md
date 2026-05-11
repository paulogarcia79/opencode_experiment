## Parent

PRD: Password Reset Flow (prd/PRD-password-reset.md)

## What to build

Build the Forgot Password page in the frontend. This includes the `ForgotPasswordView.vue` component with an email input form, the `forgotPassword()` function in `useAdminApi.ts`, the router route, and Vitest tests. The page submits to the forgot-password endpoint and shows a success message or error state.

## Acceptance criteria

- [x] `forgotPassword(email)` function added to `frontend/src/composables/useAdminApi.ts`
- [x] `ForgotPasswordView.vue` created with email input and submit button
- [x] Form calls `forgotPassword` API on submission
- [x] Shows "check your email" success message after successful submission
- [x] Shows error state on API failure
- [x] Shows loading spinner during submission
- [x] Styled consistently with `AdminLoginView.vue` (dark tech aesthetic, Tailwind)
- [x] Router route `/admin/forgot-password` added as public route (`meta: { public: true }`)
- [x] `frontend/src/views/__tests__/ForgotPasswordView.spec.ts` — tests rendering, form submission, success message, error state
- [x] `cd frontend && npm run test` passes
- [x] `cd frontend && npm run build` passes (vue-tsc type-check)

## Blocked by

- #21-forgot-password-endpoint.md
