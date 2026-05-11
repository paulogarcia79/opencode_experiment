# PRD: Rich Email Templates

## Problem Statement
Currently, the platform sends emails (newsletters and confirmations) using basic, hardcoded HTML with inline styles. These emails lack professional branding, are difficult to maintain, and may not render correctly across various email clients and mobile devices. There is no easy way for developers or admins to preview changes to the email design without sending actual test emails.

## Solution
Implement a professional email templating system using **MJML** for responsive design and **Jinja2** for dynamic content injection. This system will allow for consistent branding via a shared base layout and provide a dedicated admin endpoint for previewing templates in the browser.

## User Stories
1. As an admin, I want my newsletters to look professional and branded on all devices, so that I can build trust with my audience.
2. As a subscriber, I want to receive readable and well-formatted confirmation emails, so that I can easily complete my signup process.
3. As an admin, I want to update the site logo or brand color in one place and have it reflect in all emails, so that I can maintain a consistent brand identity.
4. As a developer, I want to use a high-level markup language (MJML) instead of complex HTML tables, so that I can create responsive layouts quickly and reliably.
5. As a developer, I want an API endpoint to preview email templates with mock data, so that I can iterate on designs without sending actual emails.
6. As a subscriber, I want the email footer to contain a clear and functional unsubscribe link, so that I can manage my preferences easily.

## Implementation Decisions

### 1. Technology Stack
- **MJML**: Used for responsive email layout generation.
- **Jinja2**: Used as a pre-processor for MJML files to handle inheritance, logic, and variable interpolation.
- **mjml-python**: Backend library to compile MJML to compatible HTML on-the-fly.

### 2. Module: Email Renderer (`app/services/email_renderer.py`)
- A new deep module responsible for the entire rendering pipeline.
- Input: Template name and a dictionary of context data.
- Process: Load MJML file → Run through Jinja2 with context → Compile resulting MJML to HTML → Return final string.

### 3. Template Architecture
- **Base Layout (`base.mjml`)**: Contains shared elements like the `<mj-head>`, brand logo, typography, and footer.
- **Specific Templates**: `newsletter.mjml` and `confirmation.mjml` will inherit from or be included in the base layout.
- **Storage**: Templates will be stored as files in `app/templates/email/`.

### 4. Configuration & Branding
- Branding constants (e.g., `BRAND_PRIMARY_COLOR`, `SITE_NAME`, `LOGO_URL`) will be added to `app/config.py` and automatically injected into every email's Jinja2 context.

### 5. Admin Preview API
- **Endpoint**: `GET /api/admin/templates/preview/{template_name}`
- **Auth**: Restricted to admin users.
- **Behavior**: Returns the rendered HTML of the requested template with placeholder data for immediate browser visualization.

## Testing Decisions
- **Renderer Unit Tests**: Verify that the renderer correctly handles Jinja2 logic (e.g., loops for tags) and compiles valid MJML.
- **Snapshot Testing**: (Optional) Verify that the generated HTML output matches expected structures for common email clients.
- **Integration Tests**: Update existing email service tests to ensure the new renderer is called with the correct parameters.

## Out of Scope
- A web-based "drag-and-drop" email builder for admins.
- Support for multiple different "themes" selectable per newsletter.
- Hosting images on external CDNs (will use existing local storage).

## Further Notes
- MJML compilation can be CPU-intensive; however, since all email sending is now offloaded to background workers, this will not affect API response times.
