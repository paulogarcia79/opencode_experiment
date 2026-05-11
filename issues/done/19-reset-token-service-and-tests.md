## Parent

PRD: Password Reset Flow (prd/PRD-password-reset.md)

## What to build

Implement the core password reset token logic in AuthService. This includes generating cryptographically random tokens, hashing them with bcrypt for secure storage, validating tokens against stored hashes with expiry checks, resetting passwords, and invalidating all pending reset tokens. The full reset token lifecycle is tested end-to-end.

## Acceptance criteria

- [x] `generate_reset_token(user)` — generates token via `secrets.token_urlsafe(32)`, hashes with bcrypt, stores hash + 15-minute expiry on user, returns plaintext token
- [x] `validate_reset_token(token)` — compares submitted token against stored hash, checks expiry, returns user or None
- [x] `reset_password(user, new_password)` — updates hashed password, increments `token_version`, calls `invalidate_all_reset_tokens()`
- [x] `invalidate_all_reset_tokens(user)` — clears `reset_token_hash` and `reset_token_expires_at` for the user
- [x] Tests: valid token generation and validation
- [x] Tests: expired token is rejected
- [x] Tests: invalid/malformed token is rejected
- [x] Tests: token is single-use (cleared after reset)
- [x] Tests: `reset_password` increments `token_version`
- [x] `just test` passes

## Blocked by

- #18-reset-db-schema-and-session-invalidation.md
