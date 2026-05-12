# QA Checklist: OAuth/SSO Integration

## 1. Prerequisites & Setup

- [ ] Docker dev stack running (`just dev-up`)
- [ ] Database migrated (`just migrate-docker`)
- [ ] `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` set in `.env` (or empty — buttons still render)
- [ ] `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` set in `.env` (or empty — buttons still render)
- [ ] Admin user exists and is verified (`is_verified = true` in `users` table)
- [ ] Resend API key configured (for email verification flow testing)

---

## 2. Backend API Checks

### OAuth Initiation
- [ ] **GET** `/api/auth/oauth/google` → **307** redirect to `accounts.google.com` with `state=` param
- [ ] **GET** `/api/auth/oauth/github` → **307** redirect to `github.com/login/oauth/authorize` with `state=` param
- [ ] **GET** `/api/auth/oauth/twitter` → **404** (unsupported provider)

### OAuth Callback
- [ ] **GET** `/api/auth/oauth/google/callback?code=xxx&state=xxx` → **302** redirect to frontend with `oauth_token=` JWT (existing user) or `verify-email?email=` (new user)
- [ ] **GET** `/api/auth/oauth/github/callback?code=xxx&state=xxx` → same behavior as Google
- [ ] Callback with invalid/missing `state` → **400**

### Email Verification
- [ ] **POST** `/api/auth/verify-email` with valid token → **200**, returns `{token, type: "bearer"}`, user becomes verified
- [ ] **POST** `/api/auth/verify-email` with invalid token → **400** `"Invalid or expired"`
- [ ] **POST** `/api/auth/verify-email` with expired token → **400**
- [ ] **POST** `/api/auth/verify-email` for already-verified user → **400**
- [ ] **POST** `/api/auth/resend-verification` with valid email → **200**, sends email
- [ ] **POST** `/api/auth/resend-verification` twice within 60s → **429**
- [ ] **POST** `/api/auth/resend-verification` with nonexistent email → **200** (no enumeration)

### Settings
- [ ] **GET** `/api/admin/settings/accounts` with valid admin token → **200**, returns `{email, is_verified, connected_providers: [...]}`
- [ ] **GET** `/api/admin/settings/accounts` without token → **401**
- [ ] **DELETE** `/api/admin/settings/accounts/oauth/google` when connected → **200**, provider removed
- [ ] **DELETE** `/api/admin/settings/accounts/oauth/google` when not connected → **404**
- [ ] **DELETE** `/api/admin/settings/accounts/oauth/google` when it's the only login method → **400** `"only login method"`

### Admin Protection
- [ ] Unverified user with valid JWT accessing `/api/admin/articles` → **401** `"Email not verified"`
- [ ] Verified user with valid JWT accessing `/api/admin/articles` → **200**

---

## 3. Frontend UI Checks

### Login Page (`/admin/login`)
- [ ] Page renders with email + password form (existing behavior intact)
- [ ] "or continue with" divider visible below login form
- [ ] Google button renders with Google icon
- [ ] GitHub button renders with GitHub icon
- [ ] Clicking Google button redirects browser to `/api/auth/oauth/google`
- [ ] Clicking GitHub button redirects browser to `/api/auth/oauth/github`
- [ ] Existing email/password login still works

### Verify Email Page (`/admin/verify-email`)
- [ ] Page accessible without auth (public route)
- [ ] Displays "Check Your Inbox" heading
- [ ] Shows the email address from URL query param (`?email=xxx`)
- [ ] "Resend Verification Email" button visible
- [ ] Clicking resend shows success message on 200 response
- [ ] Clicking resend shows error message on 429 response
- [ ] "Back to login" link navigates to `/admin/login`

### OAuth Token Handling
- [ ] Visiting `/admin?oauth_token=xxx` stores token in localStorage and redirects to `/admin`
- [ ] After redirect, admin dashboard loads with authenticated state

### Settings Page (`/admin/settings`)
- [ ] "Settings" link visible in admin navigation bar
- [ ] Clicking Settings navigates to `/admin/settings`
- [ ] Page shows user email address
- [ ] Google row shows "Connected" + "Disconnect" button if linked
- [ ] Google row shows "Connect" link if not linked
- [ ] GitHub row shows "Connected" + "Disconnect" button if linked
- [ ] GitHub row shows "Connect" link if not linked
- [ ] Clicking "Connect" redirects to provider OAuth flow
- [ ] Clicking "Disconnect" removes provider and refreshes list
- [ ] Disconnect of only login method shows error message
- [ ] After OAuth connect callback, page shows success message (`?connected=google`)

---

## 4. Edge Cases & Error Handling

- [ ] OAuth callback with missing `code` param → **400**
- [ ] OAuth callback with expired/revoked state → **400**
- [ ] OAuth callback when provider not configured (empty env vars) → **500** or graceful error
- [ ] Email verification token reused after successful verification → **400**
- [ ] Resend verification for already-verified user → **200** but no email sent
- [ ] Settings page accessed without auth → redirected to `/admin/login`
- [ ] Disconnect button clicked rapidly → loading state prevents double-click
- [ ] Network failure during resend → error message displayed
- [ ] OAuth login with email that exists but has different case → auto-links (case-insensitive)

---

## 5. Integration Checks

### End-to-End: New User via OAuth
1. Click "Sign in with Google" on login page
2. Complete Google authorization
3. → Redirected to `/admin/verify-email?email=xxx`
4. Check email inbox for verification email
5. Click verification link in email
6. → Redirected to `/admin` dashboard, fully authenticated

### End-to-End: Existing User Links OAuth
1. Log in with email/password as existing admin
2. Navigate to Settings
3. Click "Connect" on Google
4. Complete Google authorization
5. → Redirected back to Settings with success message
6. Google row shows "Connected" + "Disconnect"
7. Log out, then click "Sign in with Google"
8. → Logged in directly to dashboard (no verification needed)

### End-to-End: Disconnect Protection
1. Create OAuth-only user (no real password)
2. Navigate to Settings
3. Click "Disconnect" on the only connected provider
4. → Error message: "Cannot disconnect your only login method"
5. Provider remains connected

### Database State
- [ ] After OAuth login for new user: `users` table has new row with `is_verified=false`, `hashed_password` starts with `oauth-only:`
- [ ] After OAuth login for existing user: `user_oauth_providers` table has new row linking user to provider
- [ ] After email verification: `is_verified=true`, `verification_token_hash=NULL`
- [ ] After disconnect: `user_oauth_providers` row deleted
