## Why

Our publishing strategy is fragmented across generic platforms that don't reflect our scientific, laboratory-like identity. We need a unified Blog + Newsletter platform to control the reading experience, retain subscribers, and deliver highly detailed technical content with precision.

## What Changes

- **Article Management**: Full CRUD for blog posts with a distraction-free WYSIWYG editor (TipTap), human-readable slugs, and draft/publish lifecycle.
- **Subscriber Management**: Double opt-in email capture with confirmation workflow, one-click unsubscribe, and status tracking (pending/active/unsubscribed).
- **Newsletter Delivery**: Auto-send full article HTML to active subscribers on first publish (with per-article opt-out), powered by Resend.
- **Admin Panel**: Protected article editor and subscriber management behind bearer token authentication.
- **Public Blog**: Laboratory-aesthetic reader view with triple-coded accessibility (color + icon + pattern).

## Capabilities

### New Capabilities
- `article-management`: CRUD operations, TipTap JSON content storage, slug generation, draft/publish lifecycle
- `subscriber-management`: Double opt-in confirmation, unsubscribe workflow, status state machine
- `newsletter-delivery`: Resend integration, auto-trigger on publish, sent timestamp tracking
- `admin-authentication`: Bearer token middleware, seeded default admin user

### Modified Capabilities
- None

## Impact

New FastAPI backend with SQLModel/PostgreSQL, Vue 3 frontend with TipTap, Resend API dependency, Docker Compose services for dev/prod.

## Non-goals

- OAuth/password login (deferred to auth change)
- Image upload (external URLs only in MVP)
- RSS feed, SEO meta tags, OpenGraph
- Background job queue (synchronous delivery in MVP)
- Tags, categories, scheduled publishing
- Email open/click/bounce tracking
