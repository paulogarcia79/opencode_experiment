# Issue 43: User Management API + Invite Flow

## Parent

Issue #38: Multi-author Support

## What to build

Create the user management backend: a new `app/routers/users.py` router with endpoints to list users, invite new users via email, change roles, and toggle active status. Implement `user_management_service.py` as a deep module handling invitation generation, role updates, and activation toggles. The invite flow generates a temporary setup token, emails a setup link, and the new user sets their password via a new setup endpoint (similar to password reset flow).

## Acceptance criteria

- [ ] `GET /api/admin/users` returns list of all users with `{ id, email, role, is_active, is_verified, created_at }` (admin only)
- [ ] `POST /api/admin/users/invite` accepts `{ email, role }`, generates setup token, sends email, returns success (admin only)
- [ ] `PUT /api/admin/users/{id}/role` accepts `{ role }`, updates user role (admin only)
- [ ] `PUT /api/admin/users/{id}/active` accepts `{ is_active }`, toggles active status (admin only)
- [ ] `POST /api/auth/setup` accepts `{ token, password }`, validates setup token, sets password, marks user verified (public endpoint)
- [ ] Setup token has 24-hour expiry, single-use, invalidated after successful setup
- [ ] Invite email uses existing MJML + Jinja2 pipeline with setup link
- [ ] `app/services/user_management_service.py` encapsulates invite/update/toggle logic
- [ ] Rate limiting on invite endpoint (prevent abuse)
- [ ] Inactive users cannot login (401 with clear message)
- [ ] Tests for all user management endpoints
- [ ] Tests for user_management_service (invite flow, role update, toggle active)
- [ ] Tests for setup endpoint (valid token, expired token, reused token)
- [ ] Tests verify inactive user cannot authenticate

## Blocked by

- Issue #39: Role Model Migration + Permission Service
- Issue #41: Auth Me Endpoint + Frontend Role Store
