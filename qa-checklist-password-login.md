# QA Checklist: Password-based Login UI

## Prerequisites & Setup

- [ ] Ensure the backend server is running (`just back` or via Docker).
- [ ] Ensure the frontend server is running (`just front`).
- [ ] Ensure the database is running and migrations are applied (`just db` / `just migrate`).
- [ ] Ensure the initial admin user is seeded (default credentials: `admin@example.com` / `admin`).

## Backend API Checks

- [ ] **Action:** Send a `POST` request to `/api/auth/login` with payload `{"email": "admin@example.com", "password": "admin"}` → **Expected:** Returns `200 OK` with JSON `{ "token": "<jwt_string>", "type": "bearer" }`.
- [ ] **Action:** Send a `GET` request to `/api/admin/articles` without an Authorization header → **Expected:** Returns `403 Forbidden` with detail "Not authenticated".
- [ ] **Action:** Send a `GET` request to `/api/admin/articles` with an invalid token (e.g., `Bearer invalid_token_xyz`) → **Expected:** Returns `403 Forbidden` with detail "Invalid token" or "Invalid token payload".
- [ ] **Action:** Send a `GET` request to `/api/admin/articles` using the old `ADMIN_API_TOKEN` format (e.g., `Bearer dev-token-change-in-production`) → **Expected:** Returns `403 Forbidden` (it is no longer accepted).

## Frontend UI Checks

- [ ] **Action:** Open a browser and navigate to `/admin` without being logged in → **Expected:** Redirects to the login page (`/admin/login`).
- [ ] **Action:** On the login page, observe the input fields → **Expected:** Displays "Email" and "Password" input fields (not an "API Token" field).
- [ ] **Action:** Enter `admin@example.com` and `admin`, then click "Login" → **Expected:** The button shows a loading state ("Signing in..."), then successfully redirects to the `/admin` dashboard.
- [ ] **Action:** After logging in, refresh the page on `/admin` → **Expected:** The user remains logged in and views the dashboard without being redirected.
- [ ] **Action:** Click "Logout" (if a logout button exists in the admin layout) or manually clear `admin_token` from `localStorage` and refresh → **Expected:** User is logged out and redirected to the login page.

## Edge Cases & Error Handling

- [ ] **Action:** On the login page, submit the form with an empty email or password → **Expected:** HTML5 validation prevents submission and prompts the user to fill out the fields.
- [ ] **Action:** Enter a valid email but incorrect password (e.g., `admin@example.com` / `wrongpassword`) and submit → **Expected:** An error banner appears stating "Login Failed: Incorrect email or password".
- [ ] **Action:** Enter an unregistered email (e.g., `nonexistent@example.com`) and submit → **Expected:** An error banner appears stating "Login Failed: Incorrect email or password".
- [ ] **Action:** Simulate a network failure (disconnect from internet or stop the backend server) and attempt login → **Expected:** An error banner appears stating "Login Failed: Failed to fetch" or similar network error.

## Integration Checks

- [ ] **Action:** Complete a successful login flow, then attempt an admin action (e.g., create a draft article) → **Expected:** The action succeeds, confirming the frontend correctly attaches the new JWT to subsequent API calls.
- [ ] **Action:** Attempt to login from multiple browser tabs/windows simultaneously → **Expected:** Login succeeds in both, and the token is valid for session use across the browser.
- [ ] **Action:** Check browser `localStorage` after a successful login → **Expected:** A key named `admin_token` exists containing a valid three-part JWT string.
