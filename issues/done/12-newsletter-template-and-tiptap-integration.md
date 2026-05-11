## Parent

[PRD-rich-email-templates.md](../prd/PRD-rich-email-templates.md)

## What to build

Implement the rich newsletter template and integrate it into the background delivery worker. This slice ensures that TipTap content is correctly wrapped in a professional MJML layout.

## Acceptance criteria

- [ ] `app/templates/email/newsletter.mjml` created, inheriting from the base layout and accepting `article_html`.
- [ ] `app/worker.py`: `send_single_email_task` updated to use `EmailRenderer` with the newsletter template.
- [ ] Unsubscribe link in the footer correctly injected via Jinja2 context.
- [ ] Article title and other metadata correctly reflected in the rendered output.

## Blocked by

- [11-base-layout-and-confirmation-template.md](./11-base-layout-and-confirmation-template.md)
