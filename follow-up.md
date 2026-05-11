# Follow-up: Blog + Newsletter Platform

Items discussed during the `blog-newsletter-platform` change that were intentionally deferred or discovered as natural next steps.

---

## Authentication & Authorization

- [x] **Password-based login UI** — Replace bearer token with real username/password auth (JWT implemented)
- [x] **Password reset flow** — Email-based password reset for admin users (token-in-link, 15-min expiry, session invalidation via token_version, per-email cooldown, MJML email template)
- [ ] **OAuth / SSO integration** — Google, GitHub, or Slack OAuth for admin access
- [ ] **Multi-author support** — Multiple users with roles (admin, editor, contributor)
- [ ] **Audit logging** — Track which admin performed each action

## Content Management

- [x] **Image upload** — Drag-and-drop image upload to local storage with custom TipTap node (S3 backend still pending)
- [x] **Tags and categories** — Taxonomy system for organizing articles (flat many-to-many tags with hybrid autocomplete input, tag pages, admin management, tag-aware search)
- [x] **Scheduled publishing** — Publish articles at a future date/time (Integrated with ARQ background queue)
- [x] **Auto-save drafts** — Periodic auto-save while editing to prevent data loss (2s debounce + 30s heartbeat, retry with exponential backoff, new-article creation with deferral)
- [ ] **Revision history** — Track and restore previous versions of articles
- [ ] **Markdown import** — Import articles from Markdown files
- [ ] **Article series / collections** — Group related articles into numbered series

## Newsletter & Email

- [x] **Rich email templates** — Branded MJML + Jinja2 templates with responsive layout and admin preview API
- [x] **Email open/click tracking** — Resend webhook integration for engagement analytics (Opens, Clicks, CTR, Open Rate)
- [x] **Bounce handling** — Automatically mark bounced emails as unsubscribed (Svix signature verification, idempotency via svix_id, permanent bounce → unsubscribe, complaint → unsubscribe, bounce/complaint rate in analytics)
- [x] **Background job queue** — Redis + ARQ for reliable newsletter delivery at scale (Fan-out pattern, real-time progress tracking, automatic retries)
- [ ] **Subscriber segmentation** — Tag-based segments for targeted newsletters
- [ ] **A/B testing** — Test subject lines or content variations
- [x] **Preview email** — Send test newsletter to admin before publishing

## Public Site & SEO

- [x] **RSS / Atom feed** — `/feed.xml` for RSS readers
- [x] **SEO meta tags** — Title, description, canonical URLs
- [x] **Structured data (JSON-LD)** — Schema.org Article markup on article pages, WebSite + SearchAction on homepage
- [x] **OpenGraph / Twitter Cards** — Social sharing previews with images
- [x] **Sitemap generation** — XML sitemap for search engines (`/sitemap.xml` with published articles, homepage, RSS feed; `<lastmod>` only)
- [x] **Full-text search** — Search across article titles, descriptions, content, and tags (`/api/articles/search?q=term`, SQLite LIKE fallback + PostgreSQL tsvector ready, relevance-ranked with tag matches scoring below title/description)
- [x] **Social sharing buttons** — Share to Twitter/X, LinkedIn, Copy link on article detail page with UTM tracking
- [x] **Reading time estimate** — Display estimated reading time per article

## Analytics & Dashboard

- [x] **Subscriber analytics** — Growth charts, churn rate, active subscriber count (Interactive Admin Dashboard with Chart.js)
- [ ] **Article performance** — Views, newsletter open rates, click-through rates
- [ ] **Popular articles** — Most-read articles list
- [ ] **Referral tracking** — Where subscribers are coming from

## Infrastructure & DevEx

- [x] **Frontend tests** — Vitest + Vue Test Utils for components and composables (20 test files, 116 tests: admin store, useAdminApi, useTagSearch, NewsletterForm, TipTapRenderer, ArticleView, AdminArticlesView, AdminArticleEditView, useHead JSON-LD + prior coverage)
- [ ] **TipTapEditor tests** — Deferred due to @tiptap/vue-3 mocking complexity
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
