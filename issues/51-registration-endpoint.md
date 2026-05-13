## Parent

PRD: `prd/PRD-public-registration-and-landing-auth.md`

## What to build

Build the `POST /api/auth/register` endpoint. A visitor submits email, password, and confirm_password. The endpoint validates password complexity (8+ chars, 1 uppercase, 1 lowercase, 1 digit), enforces a 60-second IP cooldown, and creates a User with `role="contributor"` and `is_verified=False`. On success, it sends a verification email, returns `{"token": "...", "type": "bearer"}` with an `X-Registration-New: true` response header, and the user is auto-logged in. If the email is already registered, it returns a generic 200 success with no token (silent duplicate). If the requester is already authenticated, it returns 400. Server-side password validation acts as a backstop to the frontend validation.

## Acceptance criteria

- [ ] `POST /api/auth/register` accepts `{"email": "...", "password": "...", "confirm_password": "..."}`
- [ ] Password complexity enforced server-side: min 8 chars, 1 uppercase, 1 lowercase, 1 digit
- [ ] `confirm_password` must match `password` or 422 is returned
- [ ] New user created with `role="contributor"` and `is_verified=False`
- [ ] Verification email is triggered (via `send_verification_email()`)
- [ ] Response is `{"token": "...", "type": "bearer"}` with `X-Registration-New: true` header
- [ ] Duplicate email returns 200 with `{"detail": "If that email is not already registered, check your inbox."}` and no token
- [ ] 60-second IP cooldown enforced between registration attempts
- [ ] Already-authenticated requests rejected with 400
- [ ] Backend tests (pytest) cover all cases: success, duplicate, weak password, mismatch confirm, IP cooldown, authenticated rejection, role defaults to contributor
- [ ] New `RegisterRequest` Pydantic schema defined with field-level validation

## Blocked by

None — can start immediately.
