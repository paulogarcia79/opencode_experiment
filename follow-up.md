# Follow-up: Blog + Newsletter Platform

Items discussed during the `blog-newsletter-platform` change that were intentionally deferred or discovered as natural next steps.

---

## Authentication & Authorization

- [ ] **Password-based login UI** — Replace bearer token with real username/password auth
- [ ] **Password reset flow** — Email-based password reset for admin users
- [ ] **OAuth / SSO integration** — Google, GitHub, or Slack OAuth for admin access
- [ ] **Multi-author support** — Multiple users with roles (admin, editor, contributor)
- [ ] **Audit logging** — Track which admin performed each action

## Content Management

- [x] **Image upload** — Drag-and-drop image upload to local storage with custom TipTap node (S3 backend still pending)
- [x] **Tags and categories** — Taxonomy system for organizing articles (flat many-to-many tags with hybrid autocomplete input, tag pages, admin management, tag-aware search)
- [ ] **Article series / collections** — Group related articles into numbered series
- [ ] **Scheduled publishing** — Publish articles at a future date/time
- [x] **Auto-save drafts** — Periodic auto-save while editing to prevent data loss (2s debounce + 30s heartbeat, retry with exponential backoff, new-article creation with deferral)
- [ ] **Revision history** — Track and restore previous versions of articles
- [ ] **Markdown import** — Import articles from Markdown files

## Newsletter & Email

- [ ] **Rich email templates** — Branded HTML email templates instead of inline styles
- [ ] **Email open/click tracking** — Resend webhook integration for analytics
- [ ] **Bounce handling** — Automatically mark bounced emails as unsubscribed
- [ ] **Background job queue** — Redis + Celery/ARQ for reliable newsletter delivery at scale
- [ ] **Subscriber segmentation** — Tag-based segments for targeted newsletters
- [ ] **A/B testing** — Test subject lines or content variations
- [ ] **Preview email** — Send test newsletter to admin before publishing

## Public Site & SEO

- [x] **RSS / Atom feed** — `/feed.xml` for RSS readers
- [x] **SEO meta tags** — Title, description, canonical URLs, structured data
- [x] **OpenGraph / Twitter Cards** — Social sharing previews with images
- [x] **Sitemap generation** — XML sitemap for search engines (`/sitemap.xml` with published articles, homepage, RSS feed; `<lastmod>` only)
- [x] **Full-text search** — Search across article titles, descriptions, content, and tags (`/api/articles/search?q=term`, SQLite LIKE fallback + PostgreSQL tsvector ready, relevance-ranked with tag matches scoring below title/description)
- [x] **Social sharing buttons** — Share to Twitter/X, LinkedIn, Copy link on article detail page with UTM tracking
- [x] **Reading time estimate** — Display estimated reading time per article

## Analytics & Dashboard

- [ ] **Subscriber analytics** — Growth charts, churn rate, active subscriber count
- [ ] **Article performance** — Views, newsletter open rates, click-through rates
- [ ] **Popular articles** — Most-read articles list
- [ ] **Referral tracking** — Where subscribers are coming from

## Infrastructure & DevEx

- [x] **Frontend tests** — Vitest + Vue Test Utils for components and composables (coverage: useImageUpload, AdminMediaView, useHead, useReadingTime — more views needed)
- [ ] **E2E tests** — Playwright tests for critical user flows
- [ ] **API rate limiting** — Protect public endpoints from abuse
- [ ] **Caching layer** — Redis caching for published articles and lists
- [ ] **CDN integration** — CloudFront/Cloudflare for static assets
- [ ] **Backup strategy** — Automated PostgreSQL backups
- [ ] **Monitoring / alerting** — Uptime monitoring, error tracking (Sentry)
- [ ] **Webhook integrations** — Slack notification on new article publish
- [ ] **CI/CD pipeline** — GitHub Actions for testing and deployment

---

## Notes

- Priority order should be determined by user needs, not this list
- Each item above should become its own OpenSpec change when picked up
- Some items are quick patches (RSS feed), others are architectural (background queue)
