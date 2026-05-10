# [Slice 5a] Sitemap Endpoint (`/sitemap.xml`)

**GitHub Issue:** #005
**Labels:** needs-triage
**State:** open

## Parent

PRD: Sitemap and Robots.txt (`PRD-sitemap-and-robots-txt.md`)

## What to build

A public `GET /sitemap.xml` endpoint that dynamically generates a valid XML sitemap from published articles. The sitemap includes the homepage, all published article URLs, and the RSS feed, each with a `<lastmod>` timestamp. Draft articles are excluded. A code comment notes the 50,000 URL limit for future pagination.

## Acceptance criteria

- [ ] `GET /sitemap.xml` returns `200 OK` with `Content-Type: application/xml`
- [ ] XML root is `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`
- [ ] Sitemap includes homepage (`/`), all published articles (`/articles/<slug>`), and RSS feed (`/feed.xml`)
- [ ] Each `<url>` contains `<loc>` and `<lastmod>` only (no `<changefreq>`, no `<priority>`)
- [ ] Homepage `<lastmod>` uses the most recent `published_at` across all articles
- [ ] Article `<lastmod>` uses `article.updated_at`
- [ ] Draft articles are excluded from the sitemap
- [ ] Code comment notes the 50,000 URL protocol limit for future `<sitemapindex>` splitting
- [ ] Nginx dev and prod configs route `/sitemap.xml` to the backend
- [ ] Tests verify sitemap structure, content, lastmod values, and draft exclusion

## Blocked by

None - can start immediately
