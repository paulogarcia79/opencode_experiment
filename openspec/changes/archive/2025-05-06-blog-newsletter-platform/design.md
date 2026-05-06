## Context

This repository currently contains no application code — only the OpenSpec planning layer. We are building a unified Blog + Newsletter platform from scratch using the spec-driven workflow.

## Goals / Non-Goals

**Goals:**
- Public blog with laboratory aesthetic and triple-coded accessibility
- Admin panel with TipTap WYSIWYG editor for article CRUD
- Newsletter subscription with double opt-in and one-click unsubscribe
- Automatic newsletter delivery on article publish via Resend
- Bearer-token-protected admin routes with seeded default admin

**Non-Goals:**
- OAuth/password login, image upload, RSS feed, SEO/OpenGraph, background job queue, tags/categories, scheduled publishing, email open/click tracking

## Decisions

### Content Storage: TipTap JSON
- **Decision**: Store article content as TipTap JSON document (text column), render HTML on-the-fly for public view and newsletters.
- **Rationale**: Source of truth for both web and email rendering. TipTap is headless, giving full control over the lab aesthetic. Adding a cached HTML column later is trivial if needed.

### Email Delivery: Resend, Synchronous
- **Decision**: Use Resend API with synchronous calls from the publish endpoint.
- **Rationale**: Resend has a modern Python SDK and generous free tier. Synchronous delivery avoids adding Redis/Celery infrastructure for MVP scale (< 1,000 subscribers). If scale exceeds this, adding a background queue later requires no schema changes.

### Admin Authentication: Bearer Token
- **Decision**: Protect admin routes with a single `ADMIN_API_TOKEN` env variable checked via FastAPI dependency.
- **Rationale**: Zero login UI, zero session storage, trivial to rotate. The `User` table exists from day one to avoid a painful migration when real auth is added later.

### Subscriber Lifecycle: Double Opt-in, Soft Unsubscribe
- **Decision**: `pending` → `active` via confirmation email link. Unsubscribe sets `unsubscribed` status (soft delete).
- **Rationale**: Double opt-in keeps list quality high and avoids spam complaints that hurt Resend deliverability. Soft unsubscribe preserves history and is legally required in most jurisdictions.

### Article URLs: Human-Readable Slugs
- **Decision**: URLs use `/<slug>` format derived from title with uniqueness constraint and `-N` collision suffix.
- **Rationale**: Standard blog behavior, SEO-friendly, and expected by readers.

### Images: External URLs Only
- **Decision**: TipTap image node accepts external URLs only. No upload endpoint in MVP.
- **Rationale**: Keeps MVP lean while still allowing rich articles. Upload can be added later without schema changes since `src` just changes from external to internal URL.

## Risks / Trade-offs

- **[Risk]** Synchronous email delivery blocks the publish endpoint for large subscriber lists → **Mitigation**: Document the ~1,000 subscriber limit. Adding a queue later is a pure infrastructure change with no schema impact.
- **[Risk]** Bearer token auth is minimal and provides no audit trail of *which* admin performed an action → **Mitigation**: Acceptable for single-admin MVP. Real auth change will add audit logging.
- **[Risk]** TipTap JSON rendering to email-safe HTML may have edge cases with nested styles → **Mitigation**: Use a dedicated TipTap-to-email-HTML renderer (e.g., `@tiptap/html` with inline styles) and test with Resend's email preview.
