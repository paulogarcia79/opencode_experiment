## Parent

- PRD: OAuth/SSO Integration (`.opencode/plans/oauth-sso-integration.md`)

## What to build

Add the database foundation for OAuth/SSO and email verification. This includes extending the User model with verification fields, creating a new UserOAuthProvider model to track OAuth connections, generating the Alembic migration, and grandfathering the seed admin as verified.

## Acceptance criteria

- [ ] User model has `is_verified` (bool, default False), `verification_token_hash` (str, nullable), `verification_token_expires_at` (datetime, nullable)
- [ ] UserOAuthProvider model exists with `id` (UUID), `user_id` (FK to User), `provider` (str), `provider_user_id` (str), `created_at` (datetime)
- [ ] Unique constraint on `(provider, provider_user_id)` in UserOAuthProvider
- [ ] `app/models/__init__.py` exports `UserOAuthProvider`
- [ ] Alembic migration generated and applies cleanly
- [ ] Seed service sets `is_verified=True` on the seed admin user
- [ ] Existing tests still pass (no regression from schema changes)

## Blocked by

None - can start immediately
