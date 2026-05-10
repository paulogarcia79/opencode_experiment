## Problem Statement

The current admin authentication relies on a static, shared API token (`ADMIN_API_TOKEN`) passed via a bearer header. The frontend login page requires the user to manually enter this long API token. This provides a poor user experience, creates security risks (rotating the token requires a backend redeployment), and completely prevents any future implementation of multi-author support where different users have unique credentials.

## Solution

Replace the static API token with a standard password-based login system using JSON Web Tokens (JWT). The backend will hash passwords using bcrypt. The frontend login view will be updated to accept an email and password. Upon successful authentication, the backend returns a signed JWT valid for 8 days, which the frontend stores and uses as the bearer token for subsequent requests. The initial admin user will be seeded using credentials configured via environment variables.

## User Stories

1. As an admin, I want to log in using an email and password, so that I don't have to remember or copy-paste a complex API token.
2. As a security-conscious site owner, I want passwords to be hashed using a strong algorithm (bcrypt), so that a database breach doesn't expose plaintext credentials.
3. As an admin, I want my login session to remain valid for several days, so that I don't have to repeatedly log in during active content creation.
4. As an admin, I want clear error messages if I enter an incorrect email or password, so that I know why my login failed.
5. As a developer, I want the initial admin account to be seeded automatically from environment variables, so that I can reliably provision new instances of the application.
6. As a developer, I want the backend API to issue standard JWTs, so that the authentication mechanism is stateless and easily scalable.
7. As a developer, I want the existing `require_admin` dependency to seamlessly decode and validate the JWT, so that existing protected endpoints remain secure without major refactoring.
8. As a frontend developer, I want the login API endpoint to accept standard JSON payloads, so that it's simple to integrate with the Vue.js client.
9. As an admin, I want the UI to be strictly focused on login right now without non-functional "Forgot Password" links, so that the interface accurately reflects current capabilities.

## Implementation Decisions

- **Dependencies**: Add `passlib[bcrypt]` for password hashing and verification. Add `pyjwt` for generating and decoding JWTs. Add these to `pyproject.toml`.
- **Environment Configuration**: Add `ADMIN_PASSWORD` and `JWT_SECRET_KEY` to `app/config.py` and `.env.example`.
- **Seeding Update**: `seed_service.py` will hash the `ADMIN_PASSWORD` using passlib and store it in the `hashed_password` field of the default admin user.
- **Auth Endpoint**: Implement a new `POST /api/auth/login` endpoint that accepts a JSON payload containing `email` and `password`. It will verify the credentials and return a JSON object with `{ "token": "...", "type": "bearer" }`.
- **JWT Configuration**: JWTs will be signed with HS256 using `JWT_SECRET_KEY`, and will have an expiration claim (`exp`) set to 8 days from issue.
- **Dependency Update**: Refactor `app/dependencies.py::require_admin`. Instead of simple string matching against `ADMIN_API_TOKEN`, it will decode the JWT, verify the signature, ensure it hasn't expired, and check that the user exists and has `is_admin=True`.
- **Frontend Login View**: Refactor `AdminLoginView.vue` to use `email` and `password` input fields instead of a single token field. Focus strictly on login.
- **Frontend API**: Add `login(email, password)` to `useAdminApi.ts`.
- **Frontend Store**: Update `admin.ts` store login/setToken method logic if needed, though it generally remains the same (storing the JWT as a string token in `localStorage`).

## Testing Decisions

- **What makes a good test**: Tests should verify the external behavior of the login process. Backend tests should make HTTP POST requests to `/api/auth/login` with correct and incorrect credentials and assert the status codes and response bodies. Frontend tests should verify form submission and proper error handling/navigation.
- **Modules to test**:
    - **Auth Router (`tests/test_auth.py`)**: Test successful login, invalid email, invalid password.
    - **Dependencies (`tests/test_dependencies.py` or existing)**: Test `require_admin` with valid JWT, expired JWT, invalid signature, and missing token.
    - **AdminLoginView (`frontend/src/views/__tests__/AdminLoginView.spec.ts`)**: Test rendering of email/password fields, successful form submission calling `login` API, handling error states, and router redirection upon success.
- **Prior art**: The backend utilizes FastAPI's `TestClient` for endpoint testing. The frontend utilizes Vitest with `@vue/test-utils` and module-level mocking for composables.

## Out of Scope

- Password reset flow ("Forgot Password" via email).
- Multi-author support (roles beyond a single global admin).
- User registration UI (users are strictly managed/seeded by the backend for now).
- OAuth or SSO integration.
- Rate limiting for the login endpoint.

## Further Notes

- The `ADMIN_API_TOKEN` environment variable can be deprecated and removed from `app/config.py` once this transition is complete.
- Be careful with `app/dependencies.py` since all admin routes rely on it. Ensure the transition to JWT doesn't accidentally expose any admin endpoints.
