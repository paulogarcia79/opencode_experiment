# PRD: OAuth/SSO Integration

## Problem Statement

As the admin of my blog platform, I want to sign in using my Google or GitHub accounts instead of typing my email and password every time. I also want to manage which authentication methods are connected to my account, and I want to ensure that new accounts verify their email before gaining access to the admin panel.

## Solution

Add OAuth/SSO authentication via Google and GitHub alongside the existing email/password login. New users created via OAuth must verify their email before accessing the admin panel. Existing users can link or unlink OAuth providers from a new settings page. The system auto-links OAuth accounts to existing users by matching email addresses.

## User Stories

1. As an admin, I want to see "Sign in with Google" and "Sign in with GitHub" buttons on the login page, so that I can choose OAuth instead of email/password
2. As an admin, I want to click "Sign in with Google" and be redirected to Google's authorization page, so that I can grant access to my account
3. As an admin, I want to click "Sign in with GitHub" and be redirected to GitHub's authorization page, so that I can grant access to my account
4. As a new user signing in with OAuth, I want to automatically have an account created, so that I don't need to manually register first
5. As a new user signing in with OAuth, I want to receive an email verification link before accessing the admin panel, so that my email is confirmed
6. As a new user who just signed in with OAuth, I want to see a "Check your inbox" page, so that I know I need to verify my email
7. As a user clicking the email verification link, I want to be automatically verified and redirected to the admin dashboard, so that I can start using the platform
8. As an existing user with a password-based account, I want to sign in with OAuth using the same email and have my accounts automatically linked, so that I can use either login method
9. As an admin, I want to visit a Settings page at `/admin/settings`, so that I can manage my connected accounts
10. As an admin on the Settings page, I want to see which OAuth providers are connected to my account, so that I know my login options
11. As an admin on the Settings page, I want to connect a new OAuth provider, so that I can add additional login methods
12. As an admin on the Settings page, I want to disconnect an OAuth provider, so that I can remove login methods I no longer use
13. As an admin with only one login method, I want to be prevented from disconnecting it, so that I don't accidentally lock myself out
14. As a user whose OAuth email doesn't match any existing account, I want the system to create a new account for me automatically, so that I can start using the platform
15. As a user with an expired verification token, I want to request a new verification email, so that I can complete the verification process
16. As a system, I want to reject OAuth logins from unverified emails, so that only legitimate users gain access

## Implementation Decisions

### Modules to Build/Modify

**Backend:**
- **OAuth Service** (new) — Deep module: `authorize(provider) -> url`, `handle_callback(provider, code) -> user_info`, `get_user_email(user_info) -> email`
- **OAuth Router** (new) — `GET /api/auth/oauth/{provider}`, `GET /api/auth/oauth/{provider}/callback`
- **Email Verification Service** (new) — Token generation, email sending, validation (same pattern as password reset)
- **User Model** (modify) — Add `is_verified`, `verification_token_hash`, `verification_token_expires_at`
- **UserOAuthProvider Model** (new) — `id`, `user_id`, `provider`, `provider_user_id`, `created_at`
- **Auth Router** (modify) — Add `POST /api/auth/verify-email`, `POST /api/auth/resend-verification`
- **Email Service** (modify) — Add `send_verification_email()`
- **Dependencies** (modify) — `require_admin` checks `is_verified`
- **Seed Service** (modify) — Grandfather seed admin with `is_verified=True`
- **Config** (modify) — Add `GOOGLE_CLIENT_ID/SECRET`, `GITHUB_CLIENT_ID/SECRET`

**Frontend:**
- **AdminLoginView** (modify) — OAuth buttons below email/password form
- **AdminSettingsView** (new) — `/admin/settings` with connected accounts management
- **VerifyEmailView** (new) — `/admin/verify-email` with resend option
- **Router** (modify) — Add settings and verify-email routes
- **useAdminApi** (modify) — OAuth and settings API functions
- **AdminLayout** (modify) — Add Settings nav link

### Database Schema

**User additions:** `is_verified` (bool), `verification_token_hash` (str), `verification_token_expires_at` (datetime)

**New UserOAuthProvider table:** `(id, user_id, provider, provider_user_id, created_at)` with unique constraint on `(provider, provider_user_id)`

### API Contracts

- `GET /api/auth/oauth/{provider}` → Redirect to provider
- `GET /api/auth/oauth/{provider}/callback` → Exchange code, redirect to frontend with JWT or verify-email page
- `POST /api/auth/verify-email` → Validate token, return JWT
- `POST /api/auth/resend-verification` → Send new verification email (60s cooldown)
- `GET /api/admin/settings/accounts` → Connected accounts info
- `POST /api/admin/settings/accounts/oauth/{provider}` → Connect provider
- `DELETE /api/admin/settings/accounts/oauth/{provider}` → Disconnect (blocked if only login method)

## Testing Decisions

**Backend (pytest):** OAuth service URL generation, callback handling, account creation/linking, email verification flow, settings endpoints, `require_admin` rejects unverified users.

**Frontend (Vitest):** LoginView OAuth buttons, VerifyEmailView message/resend, SettingsView connected accounts display and interactions.

**Prior art:** Existing auth endpoint tests, `AdminLoginView.test.ts`, `useAdminApi.test.ts`.

## Out of Scope

- Multi-author roles, OAuth refresh tokens, public site social login, passwordless magic links, SAML/enterprise SSO, profile editing, audit logging, TipTapEditor tests.

## Further Notes

- `ADMIN_API_TOKEN` env var is dead code — should be removed
- OAuth-only users need a random unusable password (field is non-nullable)
- `UserOAuthProvider` enables future provider expansion without schema changes
