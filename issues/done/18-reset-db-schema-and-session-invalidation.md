## Parent

PRD: Password Reset Flow (prd/PRD-password-reset.md)

## What to build

Add the database schema changes needed for password reset and update JWT session invalidation. This is the foundation that all other slices depend on. Add `reset_token_hash`, `reset_token_expires_at`, and `token_version` columns to the `users` table via Alembic migration. Update the `require_admin` dependency to validate that the JWT's `token_version` claim matches the user's current `token_version` in the database, enabling full session invalidation on password reset.

## Acceptance criteria

- [x] Alembic migration adds `reset_token_hash` (str, nullable), `reset_token_expires_at` (datetime, nullable), and `token_version` (int, default 0) to the `users` table
- [x] `User` model in `app/models/user.py` updated with the three new fields
- [x] `create_access_token()` in AuthService includes `token_version` in the JWT payload
- [x] `require_admin` in `app/dependencies.py` decodes `token_version` from JWT and compares it against the user's current `token_version` — rejects if mismatched
- [x] Existing auth tests still pass (valid JWT, expired JWT, missing token)
- [x] New test: JWT with stale `token_version` is rejected by `require_admin`
- [x] `just migrate` runs successfully
- [x] `just test` passes

## Blocked by

- None - can start immediately
