## Parent

[PRD-rich-email-templates.md](../prd/PRD-rich-email-templates.md)

## What to build

Setup the core infrastructure for rich email rendering. This involves adding required dependencies, defining branding configuration, and implementing the `EmailRenderer` service that handles Jinja2 pre-processing and MJML compilation.

## Acceptance criteria

- [ ] `mjml-python` and `jinja2` added to `pyproject.toml`.
- [ ] Branding constants (`BRAND_PRIMARY_COLOR`, `SITE_NAME`, `SITE_LOGO_URL`) added to `app/config.py`.
- [ ] `app/services/email_renderer.py` implemented with a `render` function that takes a template name and context.
- [ ] Directory `app/templates/email/` created.
- [ ] Unit tests for `EmailRenderer` verify Jinja2 interpolation and MJML compilation.

## Blocked by

None - can start immediately
