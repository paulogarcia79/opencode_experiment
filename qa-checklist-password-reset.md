# QA Checklist: Password Reset Flow

## 1. Prerequisites & Setup

- [ ] Backend dev server running (`just back` or `just dev`)
- [ ] Frontend dev server running (`just front` or `just dev`)
- [ ] PostgreSQL running with migrations applied (`just db && just migrate`)
- [ ] Admin user seeded (check `.env` for `ADMIN_EMAIL` / `ADMIN_PASSWORD`)
- [ ] `RESEND_API_KEY` configured in `.env` (or skip email delivery checks if not available)
- [ ] Browser open at `http://localhost:5173`

---

## 2. Backend API Checks

### POST `/api/auth/forgot-password`

- [ ] **Action:** Send `{ "email": "<admin_email>" }` → **Expected:** 200, `{ "message": "If an account exists with that email, a reset link has been sent" }`
- [ ] **Action:** Send `{ "email": "nonexistent@example.com" }` → **Expected:** 200, identical response (no email enumeration)
- [ ] **Action:** Send same email twice within 60 seconds → **Expected:** 429, `{ "detail": "Please wait before requesting another reset link." }`
- [ ] **Action:** Send empty body `{}` → **Expected:** 422 (validation error)

### POST `/api/auth/reset-password`

- [ ] **Action:** Send valid `{ "token": "<from_email>", "new_password": "newpass" }` → **Expected:** 200, `{ "message": "Password reset successfully." }`
- [ ] **Action:** Send `{ "token": "invalid-token", "new_password": "newpass" }` → **Expected:** 400, `{ "detail": "Invalid or expired reset token." }`
- [ ] **Action:** Reuse the same token after a successful reset → **Expected:** 400
- [ ] **Action:** Send empty body `{}` → **Expected:** 422 (validation error)

### Session Invalidation

- [ ] **Action:** Log in with admin credentials to get a JWT → **Expected:** 200 with token
- [ ] **Action:** Use that JWT to access `/api/admin/articles` → **Expected:** 200
- [ ] **Action:** Complete a password reset for that user → **Expected:** 200
- [ ] **Action:** Use the same JWT to access `/api/admin/articles` again → **Expected:** 401 (session invalidated)

---

## 3. Frontend UI Checks

### Forgot Password Page

- [ ] **Action:** Navigate to `/admin/forgot-password` → **Expected:** Page renders with email input, "Send Reset Link" button, "Back to login" link
- [ ] **Action:** Enter valid admin email, click "Send Reset Link" → **Expected:** Loading spinner shows ("Sending..."), then success banner: "Check your email" with message
- [ ] **Action:** After success, verify form is hidden and only success message is visible → **Expected:** Form replaced by green success banner
- [ ] **Action:** Click "Back to login" → **Expected:** Redirects to `/admin/login`

### Reset Password Page

- [ ] **Action:** Navigate to `/admin/reset-password?token=test-token` → **Expected:** Page renders with "New Password" and "Confirm Password" inputs, "Reset Password" button
- [ ] **Action:** Enter matching passwords, click "Reset Password" → **Expected:** Loading spinner shows ("Resetting..."), then redirects to `/admin/login`
- [ ] **Action:** Enter mismatching passwords, click "Reset Password" → **Expected:** Error banner: "Reset Failed" with "Passwords do not match"
- [ ] **Action:** Navigate to `/admin/reset-password` (no token) → **Expected:** Page renders; submitting form shows error "Missing reset token. Please request a new link."

### Email Delivery

- [ ] **Action:** Submit forgot-password form with valid admin email → **Expected:** Email received at admin inbox with branded template, reset link button, and "15 minutes" expiry notice
- [ ] **Action:** Click the reset link in the email → **Expected:** Browser opens `/admin/reset-password?token=<token>` with the reset password form

---

## 4. Edge Cases & Error Handling

- [ ] **Action:** Submit forgot-password with malformed email (e.g., `not-an-email`) → **Expected:** Browser validation prevents submission (HTML5 `type="email"`)
- [ ] **Action:** Submit reset-password with empty password fields → **Expected:** Browser validation prevents submission (HTML5 `required`)
- [ ] **Action:** Wait 15+ minutes, then use a reset link from email → **Expected:** Error: "Invalid or expired reset token."
- [ ] **Action:** Click the same reset link twice → **Expected:** First succeeds, second shows "Invalid or expired reset token."
- [ ] **Action:** Access `/admin/forgot-password` while already logged in → **Expected:** Redirects to `/admin` (auth guard)
- [ ] **Action:** Access `/admin/reset-password?token=xyz` while already logged in → **Expected:** Redirects to `/admin` (auth guard)
- [ ] **Action:** Backend is down, submit forgot-password form → **Expected:** Error banner: "Request Failed" with network error message

---

## 5. Integration Checks

- [ ] **Action:** Full end-to-end flow: forgot-password → receive email → click link → set new password → log in with new password → **Expected:** Login succeeds, dashboard loads
- [ ] **Action:** After password reset, try logging in with the OLD password → **Expected:** "Incorrect email or password"
- [ ] **Action:** After password reset, open a second browser tab that was previously logged in → **Expected:** Any admin action returns 401, user is effectively logged out
- [ ] **Action:** Request a new reset link while a previous one is still valid → **Expected:** New link works, old link is invalidated (only one active token per user)
