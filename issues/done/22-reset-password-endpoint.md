## Parent

PRD: Password Reset Flow (prd/PRD-password-reset.md)

## What to build

Implement the `POST /api/auth/reset-password` endpoint that validates the reset token, updates the user's password, increments `token_version` to invalidate all existing JWT sessions, and clears all pending reset tokens. The full reset flow is tested end-to-end.

## Acceptance criteria

- [x] `ResetPasswordRequest` schema added to `app/schemas.py` with `token` and `new_password` fields
- [x] `POST /api/auth/reset-password` endpoint accepts `{ "token": "...", "new_password": "..." }`
- [x] Validates token via AuthService — returns 400 if invalid or expired
- [x] On valid token: updates password, increments `token_version`, invalidates all reset tokens
- [x] Returns 200 on success
- [x] Test: successful reset → 200, password updated
- [x] Test: invalid token → 400
- [x] Test: expired token → 400
- [x] Test: token reuse after reset → 400
- [x] Test: existing JWT sessions are invalidated after reset (old token rejected by `require_admin`)
- [x] `just test` passes

## Blocked by

- #19-reset-token-service-and-tests.md
