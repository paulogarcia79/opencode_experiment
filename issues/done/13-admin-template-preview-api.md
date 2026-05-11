## Parent

[PRD-rich-email-templates.md](../prd/PRD-rich-email-templates.md)

## What to build

Expose an admin-only API endpoint to preview email templates directly in the browser. This allows developers and admins to verify designs with mock data without sending real emails.

## Acceptance criteria

- [ ] New endpoint `GET /api/admin/templates/preview/{template_name}` implemented.
- [ ] Endpoint requires admin authentication.
- [ ] Returns `Content-Type: text/html` with the fully compiled MJML output.
- [ ] Uses mock data (dummy article title, content, tokens) for the preview context.
- [ ] Endpoint is accessible via the browser or API client.

## Blocked by

- [12-newsletter-template-and-tiptap-integration.md](./12-newsletter-template-and-tiptap-integration.md)
