# Issue 41: Auth Me Endpoint + Frontend Role Store

## Parent

Issue #38: Multi-author Support

## What to build

Create a `GET /api/auth/me` endpoint that returns the current authenticated user's profile (email, role, is_active, is_verified). Extend the Pinia admin store to hold the user profile alongside the JWT token. After login, the frontend calls `/api/auth/me` to populate the store. Update router guards to be ready for role-based access checks.

## Acceptance criteria

- [ ] `GET /api/auth/me` endpoint returns `{ id, email, role, is_active, is_verified, created_at }` for the authenticated user
- [ ] `/api/auth/me` requires valid JWT (uses `require_role(["admin", "editor", "contributor"])`)
- [ ] `/api/auth/me` returns 401 for inactive users
- [ ] Pinia `admin` store has `user` ref with profile data alongside `token`
- [ ] After login (password + OAuth), frontend calls `/api/auth/me` and stores the result
- [ ] On page load with existing token, frontend calls `/api/auth/me` to restore user profile
- [ ] On logout, user profile is cleared alongside token
- [ ] Frontend `User` type defined in `types/index.ts`
- [ ] Tests for `/api/auth/me` endpoint (authenticated, unauthenticated, inactive user)
- [ ] Tests for Pinia store (set user, clear user, persist across calls)

## Blocked by

Issue #39: Role Model Migration + Permission Service
