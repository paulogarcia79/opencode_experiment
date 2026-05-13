## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Split the auth dependency layer so unverified users have a graduated experience instead of a hard 401 block. Create a new `require_role_allow_unverified` dependency that skips the `is_verified` check, and apply it to `GET /api/auth/me` and `GET /api/admin/settings/accounts`. Update the existing `require_role` dependency so that when a user is authenticated but `is_verified=False`, it returns HTTP 403 with body `{"detail": "Email not verified", "code": "EMAIL_NOT_VERIFIED"}` — distinct from the 401 for missing/bad tokens and from the 403 for insufficient role. All other authenticated endpoints keep using the strict `require_role` variant, unverified users get the new 403 error code.

## Acceptance criteria

- [ ] New `require_role_allow_unverified` dependency exists, skips `is_verified` check
- [ ] `GET /api/auth/me` uses `require_role_allow_unverified` — works for unverified users
- [ ] `GET /api/admin/settings/accounts` uses `require_role_allow_unverified` — works for unverified users
- [ ] Existing `require_role` returns HTTP 403 with `{"detail": "Email not verified", "code": "EMAIL_NOT_VERIFIED"}` when user is unverified
- [ ] All other authenticated endpoints (articles CRUD, images, etc.) continue using strict `require_role` — unverified users get the new 403
- [ ] Verified users experience no change in any endpoint behavior
- [ ] Backend tests (pytest): test `require_role_allow_unverified` passes for unverified users with valid roles
- [ ] Backend tests: test `require_role` returns 403 `EMAIL_NOT_VERIFIED` for unverified users
- [ ] Backend tests: test both dependencies pass for verified users
- [ ] Backend tests: test unauthenticated requests still get 401 from both dependencies

## Blocked by

None — can start immediately.
