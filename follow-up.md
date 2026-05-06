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

- [ ] **Image upload** — Drag-and-drop image upload to S3/local storage with custom TipTap node
- [ ] **Tags and categories** — Taxonomy system for organizing articles
- [ ] **Article series / collections** — Group related articles into numbered series
- [ ] **Scheduled publishing** — Publish articles at a future date/time
- [ ] **Auto-save drafts** — Periodic auto-save while editing to prevent data loss
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

- [ ] **RSS / Atom feed** — `/feed.xml` for RSS readers
- [ ] **SEO meta tags** — Title, description, canonical URLs, structured data
- [ ] **OpenGraph / Twitter Cards** — Social sharing previews with images
- [ ] **Sitemap generation** — XML sitemap for search engines
- [ ] **Full-text search** — Search across article titles and content
- [ ] **Social sharing buttons** — Share to Twitter/X, LinkedIn, etc.
- [ ] **Reading time estimate** — Display estimated reading time per article

## Analytics & Dashboard

- [ ] **Subscriber analytics** — Growth charts, churn rate, active subscriber count
- [ ] **Article performance** — Views, newsletter open rates, click-through rates
- [ ] **Popular articles** — Most-read articles list
- [ ] **Referral tracking** — Where subscribers are coming from

## Infrastructure & DevEx

- [ ] **Frontend tests** — Vitest + Vue Test Utils for components and composables
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
