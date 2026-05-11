## Problem Statement

As an admin user, if I forget my password, I am completely locked out of the blog and newsletter platform. There is no way to recover access without manually editing the database or redeploying with new credentials. This is a critical gap in the authentication system — password-based login was implemented, but the corresponding reset flow was intentionally deferred.

## Solution

Implement an email-based password reset flow for admin users. The admin enters their email on a "Forgot Password" page, receives a branded email with a time-limited reset link, clicks it, and sets a new password. The flow invalidates all active sessions upon reset, ensuring security if the account was compromised.

## User Stories

1. As an admin who forgot my password, I want to request a password reset via email, so that I can regain access to my account without database manipulation.
2. As an admin, I want to receive a branded, professional-looking password reset email, so that I trust the email is legitimate and not a phishing attempt.
3. As an admin, I want the reset link to work immediately when I click it, so that I can set a new password without friction.
4. As an admin, I want to enter and confirm my new password on a dedicated page, so that I avoid typos that would lock me out again.
5. As a security-conscious admin, I want the reset link to expire after a short time, so that an attacker cannot use a stale link from my inbox.
6. As an admin, I want all my existing sessions to be invalidated after I reset my password, so that if someone else was logged in, they are kicked out.
7. As an admin, I want to be able to request a new reset link if the previous one expired, so that I'm not permanently locked out if I miss the window.
8. As a developer, I want the forgot-password endpoint to return the same response regardless of whether the email exists, so that attackers cannot enumerate valid admin emails.
9. As a developer, I want the forgot-password endpoint to enforce a cooldown per email, so that the endpoint cannot be abused to flood an inbox or burn through Resend quota.
10. As a developer, I want the reset token to be hashed before storage, so that a database breach doesn't expose active reset tokens.
11. As a developer, I want the reset token to be single-use, so that once a password is reset, the same link cannot be reused.
12. As a frontend user, I want clear visual feedback during the reset process (loading states, success messages, error messages), so that I understand what's happening at each step.
13. As an admin, I want to be redirected to the login page after successfully resetting my password, so that I can immediately log in with my new credentials.
14. As a developer, I want the password reset email template to reuse the existing MJML rendering pipeline, so that branding is consistent with newsletter and confirmation emails.

## Implementation Decisions

- **Database schema**: Add three columns to the `users` table via Alembic migration:
  - `reset_token_hash` (str, nullable) — bcrypt hash of the reset token
  - `reset_token_expires_at` (datetime, nullable) — expiry timestamp for the reset token
  - `token_version` (int, default 0) — incremented on password reset to invalidate all existing JWT sessions

- **AuthService additions**: Add methods to the existing auth service:
  - `generate_reset_token(user)` — generates a cryptographically random token via `secrets.token_urlsafe(32)`, hashes it with bcrypt, stores hash + expiry (15 minutes), returns the plaintext token for email inclusion
  - `validate_reset_token(token)` — compares submitted token against stored hash, checks expiry, returns the associated user or None
  - `reset_password(user, new_password)` — updates the user's hashed password, increments `token_version`, deletes all reset tokens for the user
  - `invalidate_all_reset_tokens(user)` — clears all pending reset tokens for a user

- **Email service addition**: Add `send_password_reset_email(email, reset_token)` to `email_service.py`, using the existing `email_renderer.py` pipeline with a new `password_reset.mjml` template. The template will include the reset URL (`{app_base_url}/admin/reset-password?token={token}`), an expiry notice (15 minutes), and consistent branding via the auto-injected context variables.

- **New API endpoints**:
  - `POST /api/auth/forgot-password` — Accepts `{ "email": "..." }`. Looks up user by email. If found, generates reset token and sends email. Always returns 200 with `{ "message": "If an account exists with that email, a reset link has been sent" }` regardless of whether the email exists. Enforces a 60-second per-email cooldown (returns 429 if exceeded).
  - `POST /api/auth/reset-password` — Accepts `{ "token": "...", "new_password": "..." }`. Validates the token. If valid, resets the password, increments `token_version`, invalidates all reset tokens for the user. Returns 200 on success. Returns 400 if token is invalid or expired.

- **Cooldown implementation**: Use an in-memory dictionary mapping email → last_request_timestamp. Simple, no new dependencies, sufficient for a single-admin system. The ARQ Redis instance is available but adds unnecessary complexity for this use case.

- **JWT session invalidation**: The `require_admin` dependency in `app/dependencies.py` will be updated to also check that the JWT's `token_version` claim (added to JWT payload) matches the user's current `token_version` in the database. On password reset, `token_version` is incremented, causing all previously issued JWTs to fail validation.

- **Frontend pages**:
  - `ForgotPasswordView.vue` — Email input form. Submits to `/api/auth/forgot-password`. On success, shows a "check your email" confirmation message. Styled consistently with `AdminLoginView.vue`.
  - `ResetPasswordView.vue` — New password + confirm password form. Reads `token` from `?token=` query param on page load. Submits `{ token, new_password }` to `/api/auth/reset-password`. On success, redirects to `/admin/login` with a success indicator. Handles invalid/expired token errors gracefully.
  - Both pages reuse the dark tech aesthetic (Tailwind) from the existing admin views.

- **Frontend composables**: Add `forgotPassword(email)` and `resetPassword(token, newPassword)` functions to `useAdminApi.ts`.

- **Frontend router**: Add `/admin/forgot-password` and `/admin/reset-password` routes. Both are public routes (no auth required).

- **Schemas**: Add `ForgotPasswordRequest`, `ResetPasswordRequest`, and `ResetPasswordResponse` schemas to `app/schemas.py`.

- **No password strength validation**: The reset flow will not enforce password complexity rules, maintaining consistency with the existing password-based login implementation. This can be added as a separate feature later.

## Testing Decisions

- **What makes a good test**: Tests should verify the external behavior of the password reset flow — HTTP request/response contracts, email sending, token validation, session invalidation, and frontend form interactions. Implementation details (e.g., how the token is hashed) should not be tested directly; instead, test that valid tokens work and invalid/expired tokens are rejected.

- **Backend modules to test** (`tests/`):
  - **Auth router** (`tests/test_auth.py` or new `tests/test_password_reset.py`):
    - Successful forgot-password request → 200, email sent
    - Forgot-password for non-existent email → 200, same response (no enumeration)
    - Forgot-password cooldown → 429 after rapid requests for same email
    - Successful reset-password → 200, password updated, token invalidated
    - Reset-password with invalid token → 400
    - Reset-password with expired token → 400
    - Reset-password reusing a token → 400 (single-use enforcement)
    - Session invalidation after reset → old JWT rejected by `require_admin`
  - **AuthService** — Test token generation produces valid tokens, expiry enforcement works, hash comparison is correct. Can be tested via the endpoint tests (integration style) or as unit tests.

- **Frontend modules to test** (`frontend/src/`):
  - **ForgotPasswordView** (`frontend/src/views/__tests__/ForgotPasswordView.spec.ts`):
    - Renders email input and submit button
    - Calls `forgotPassword` API on form submission
    - Shows success message after successful submission
    - Shows error state on API failure
  - **ResetPasswordView** (`frontend/src/views/__tests__/ResetPasswordView.spec.ts`):
    - Renders password + confirm password inputs
    - Reads token from URL query param
    - Calls `resetPassword` API on form submission
    - Redirects to login on success
    - Shows error for invalid/expired token
  - **useAdminApi** — Add tests for `forgotPassword` and `resetPassword` functions (or extend existing `useAdminApi` tests).

- **Prior art**: Backend uses FastAPI `TestClient` with SQLite in-memory database (`tests/conftest.py`). Frontend uses Vitest with `@vue/test-utils` and happy-dom environment, with module-level mocking for composables. See `tests/test_auth.py` and `frontend/src/views/__tests__/AdminLoginView.spec.ts` for patterns.

## Out of Scope

- OAuth / SSO integration (Google, GitHub, Slack).
- Multi-author support with roles (admin, editor, contributor).
- Password strength / complexity validation.
- "Remember me" or persistent session management beyond JWT expiry.
- Audit logging of password reset events.
- Rate limiting by IP address (only per-email cooldown is in scope).
- Email delivery failure handling (e.g., if Resend fails to send the reset email).
- Mobile-responsive email template beyond what the existing MJML base provides.

## Further Notes

- The `token_version` field on the User model is a new concept for this codebase. It should be documented so future features (e.g., "logout all devices") can leverage it.
- The in-memory cooldown map will reset on application restart. This is acceptable for a single-admin system but should be noted. If multi-instance deployment becomes a reality, the cooldown should be moved to Redis.
- The password reset email template should be tested visually by sending a test email via the existing preview email mechanism once implemented.
- Consider adding a `password_reset_requested_at` timestamp to the user model in the future for audit purposes, but this is out of scope for the initial implementation.
