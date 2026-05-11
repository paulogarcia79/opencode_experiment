## Parent

[PRD-rich-email-templates.md](../prd/PRD-rich-email-templates.md)

## What to build

Create the responsive base layout and implement the rich confirmation email. Update the subscriber service to use the new templated email instead of hardcoded HTML.

## Acceptance criteria

- [ ] `app/templates/email/base.mjml` created with responsive header, footer, and branding.
- [ ] `app/templates/email/confirmation.mjml` created, inheriting from the base layout.
- [ ] `app/services/email_service.py` updated: `send_confirmation_email` uses `EmailRenderer`.
- [ ] Manual verification (via logs or mock) shows the confirmation email rendered as a full HTML document.

## Blocked by

- [10-email-rendering-infrastructure.md](./10-email-rendering-infrastructure.md)
