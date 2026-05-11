## Parent

PRD: Password Reset Flow (prd/PRD-password-reset.md)

## What to build

Create the password reset email template using the existing MJML + Jinja2 rendering pipeline and add the `send_password_reset_email()` function to EmailService. The email should be branded consistently with existing newsletter and confirmation emails, include the reset link with token, and display a 15-minute expiry notice.

## Acceptance criteria

- [x] `app/templates/email/password_reset.mjml` created, extending `base.mjml` with branded layout
- [x] Template includes reset URL (`{app_base_url}/admin/reset-password?token={token}`)
- [x] Template displays 15-minute expiry notice
- [x] Template uses auto-injected context variables (`site_name`, `site_logo_url`, `brand_color`, `app_base_url`, `current_year`)
- [x] `send_password_reset_email(email, reset_token)` added to `email_service.py` using existing `email_renderer.py` pipeline
- [x] Email renders correctly (MJML → HTML)
- [x] `just test` passes

## Blocked by

- None - can start immediately (independent of schema changes)
