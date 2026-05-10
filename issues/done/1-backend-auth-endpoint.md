## Parent

PRD: Password-based Login UI (prd/PRD-password-login.md)

## What to build

Establish the core backend authentication infrastructure. Add the necessary cryptographic dependencies, update the environment configuration, seed the default admin with a properly hashed password, and create the API endpoint to issue JSON Web Tokens (JWT) upon successful login. Existing admin routes will *not* be migrated to JWT in this slice to prevent prematurely breaking the frontend.

## Acceptance criteria

- [ ] `passlib[bcrypt]` and `pyjwt` added to `pyproject.toml` and installed
- [ ] `ADMIN_PASSWORD` and `JWT_SECRET_KEY` added to `app/config.py` and `.env.example`
- [ ] `seed_service.py` updated to hash `ADMIN_PASSWORD` before storing it in the database
- [ ] `auth_service.py` created with functions to verify passwords, hash passwords, and generate JWTs (HS256, 8 days expiry)
- [ ] `POST /api/auth/login` endpoint implemented accepting JSON `{"email": "...", "password": "..."}` and returning `{ "token": "...", "type": "bearer" }`
- [ ] `tests/test_auth.py` added to verify successful login, invalid email, and invalid password scenarios
- [ ] `just test` passes

## Blocked by

None - can start immediately
