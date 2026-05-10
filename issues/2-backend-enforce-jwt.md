## Parent

PRD: Password-based Login UI (prd/PRD-password-login.md)

## What to build

Secure the backend admin routes by enforcing JWT validation. Update the `require_admin` dependency to decode and verify the JWT issued by the login endpoint, replacing the old static API token check. This will break the current frontend admin panel until the UI is updated.

## Acceptance criteria

- [ ] `app/dependencies.py::require_admin` refactored to decode JWT, verify signature, check expiration, and ensure user exists with `is_admin=True`
- [ ] `ADMIN_API_TOKEN` logic completely removed from `require_admin`
- [ ] Tests added/updated to verify protected routes return `401`/`403` for missing, invalid, or expired JWTs
- [ ] Tests added/updated to verify protected routes succeed with a valid JWT
- [ ] `just test` passes

## Blocked by

- 1-backend-auth-endpoint.md
