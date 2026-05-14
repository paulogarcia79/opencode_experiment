## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Update the Pinia admin store and the API composable to support the new registration and verification flows. Add a `register(email, password, confirmPassword)` function to `useAdminApi.ts` that calls `POST /api/auth/register`, handles the token response, and detects duplicate emails (response body has no `token` field). Update `resendVerification()` to send a Bearer token instead of an email body. Add a global fetch response interceptor that catches 403 responses with error code `EMAIL_NOT_VERIFIED` and sets a reactive `verificationRequired` ref that the VerificationBanner will watch. Add `isVerificationBannerDismissed` (session-only, not persisted) to the store. Handle the `X-Registration-New` response header from registration to trigger a welcome toast.

## Acceptance criteria

- [ ] `register(email, password, confirmPassword)` function in `useAdminApi.ts`
- [ ] Register function sends correct POST payload to `/api/auth/register`
- [ ] Register function sets token and calls `fetchMe()` on success
- [ ] Register function detects duplicate email (response has no `token`) and throws/rejects with distinct error or returns `{ duplicate: true }`
- [ ] `resendVerification()` uses `Authorization: Bearer <token>` header, no longer sends email in body
- [ ] Global fetch response interceptor catches 403 `EMAIL_NOT_VERIFIED` errors
- [ ] Interceptor sets `verificationRequired` reactive ref to `true`
- [ ] `isVerificationBannerDismissed` ref in store, default `false`, clears on page refresh (not persisted to localStorage)
- [ ] `X-Registration-New` header detected after register call, triggers welcome toast via existing toast infrastructure
- [ ] Frontend tests: register sends correct payload
- [ ] Frontend tests: register handles token response (sets store, fetches profile)
- [ ] Frontend tests: register handles duplicate email (no token in response)
- [ ] Frontend tests: resend uses bearer token
- [ ] Frontend tests: 403 `EMAIL_NOT_VERIFIED` interceptor sets verification ref
- [ ] Frontend tests: banner dismissal is session-only (reset on new store instance)
- [ ] `npm run build` passes

## Blocked by

- #51 (registration endpoint must exist — tests can mock until then)
- #52 (EMAIL_NOT_VERIFIED error code must be defined)
- #53 (bearer-token resend endpoint must exist)
