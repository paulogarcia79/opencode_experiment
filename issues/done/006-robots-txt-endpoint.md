# [Slice 5b] Robots.txt Endpoint (`/robots.txt`)

**GitHub Issue:** #006
**Labels:** needs-triage
**State:** open

## Parent

PRD: Sitemap and Robots.txt (`PRD-sitemap-and-robots-txt.md`)

## What to build

A public `GET /robots.txt` endpoint that returns crawl instructions for search engine bots. It allows all public content, disallows admin/API/uploads routes, and references the sitemap location so crawlers discover it automatically.

## Acceptance criteria

- [ ] `GET /robots.txt` returns `200 OK` with `Content-Type: text/plain; charset=utf-8`
- [ ] Body contains `User-agent: *`
- [ ] Body contains `Disallow: /admin/`
- [ ] Body contains `Disallow: /api/`
- [ ] Body contains `Disallow: /uploads/`
- [ ] Body contains `Sitemap: {APP_BASE_URL}/sitemap.xml`
- [ ] Nginx dev and prod configs route `/robots.txt` to the backend
- [ ] Tests verify robots.txt content, disallowed paths, and sitemap reference

## Blocked by

- #005 ([Slice 5a] Sitemap Endpoint) — shares `app/routers/articles.py` and Nginx config files to avoid merge conflicts
