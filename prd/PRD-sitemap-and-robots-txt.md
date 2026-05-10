## Problem Statement

Search engines cannot efficiently discover all public pages on the blog. While RSS/Atom feed (`/feed.xml`) exists for feed readers, there is no XML sitemap to help search engine crawlers index the site. Additionally, there is no `robots.txt` to guide crawlers on what to index and where to find the sitemap.

This means:
- New articles may take longer to appear in search results
- There is no declarative way to tell crawlers which pages matter (homepage, articles, RSS feed)
- No crawl rules prevent indexing of admin routes, API endpoints, or raw uploads

## Solution

Add two public endpoints:
1. **`/sitemap.xml`** — a dynamic XML sitemap listing all publicly indexable URLs (homepage, published articles, RSS feed) with their last modification dates
2. **`/robots.txt`** — crawl instructions that allow all public content, disallow admin/API/uploads routes, and reference the sitemap location

## User Stories

1. As a search engine crawler, I want to discover all published article URLs via `/sitemap.xml`, so that I can index them efficiently
2. As a search engine crawler, I want to see when each article was last modified via `<lastmod>`, so that I know whether to re-crawl it
3. As a site owner, I want `/robots.txt` to disallow `/admin/`, `/api/`, and `/uploads/` from crawling, so that private or non-content URLs are not indexed
4. As a site owner, I want `/robots.txt` to reference the sitemap URL, so that crawlers discover it automatically without manual submission
5. As a site owner, I want the sitemap to include the RSS feed URL, so that crawlers know about the alternative content discovery mechanism
6. As a site owner, I want the sitemap to be dynamically generated from the database, so that it always reflects the current published state without manual updates
7. As a developer, I want a code comment noting the 50,000 URL sitemap limit, so that future maintainers know when to implement pagination or `<sitemapindex>`
8. As a developer, I want tests verifying that draft articles are excluded from the sitemap, so that unpublished content is never exposed to crawlers

## Implementation Decisions

### Modules

**Sitemap Generation Endpoint**
- Dynamic FastAPI endpoint `GET /sitemap.xml`
- Queries the existing `list_published_articles()` service function (no new DB logic needed)
- Generates XML `<urlset>` with `<url>` elements containing `<loc>` and `<lastmod>` only
- Excludes `<changefreq>` and `<priority>` (search engines ignore them)
- Homepage `<lastmod>` uses the most recent `published_at` across all articles
- Article `<lastmod>` uses `article.updated_at`
- RSS feed `<lastmod>` uses the most recent `published_at`
- Code comment documents the 50,000 URL protocol limit for future splitting

**Robots.txt Endpoint**
- Dynamic FastAPI endpoint `GET /robots.txt`
- Returns plain text with `User-agent: *`, `Disallow` rules, and `Sitemap:` reference
- Disallows: `/admin/`, `/api/`, `/uploads/`
- Sitemap reference uses `APP_BASE_URL` from settings

**Nginx Configuration**
- Both dev and prod Nginx configs route `/sitemap.xml` and `/robots.txt` to the backend
- Consistent with existing `/feed.xml` routing pattern

**Router Placement**
- Both endpoints live in the existing `articles` router alongside `/feed.xml`
- Keeps SEO-related endpoints together; avoids premature extraction into a separate router

### Schema Changes
- None. Uses existing `Article` model and `list_published_articles()` service.

### API Contracts
- `GET /sitemap.xml` → `200 OK`, `Content-Type: application/xml`
- `GET /robots.txt` → `200 OK`, `Content-Type: text/plain; charset=utf-8`

## Testing Decisions

**What makes a good test:** Test external behavior only — the XML structure, content, and exclusions — not the internal string-building logic.

**Modules to test:**
- `GET /sitemap.xml` endpoint: verify 200 status, correct content-type, contains homepage, published articles, and RSS feed URLs, excludes draft articles, includes `<lastmod>` tags
- `GET /robots.txt` endpoint: verify 200 status, correct content-type, contains `Disallow: /admin/`, `Disallow: /api/`, `Disallow: /uploads/`, and `Sitemap:` reference

**Prior art:**
- `test_rss_feed` and `test_rss_feed_excludes_drafts` in `tests/test_articles.py` follow the same pattern: create articles, publish some, verify endpoint output
- Use `TestClient` and the existing `session`/`client` pytest fixtures

## Out of Scope

- Image sitemap (`<image:image>` tags) — deferred to a follow-up when image SEO becomes a priority
- Sitemap pagination or `<sitemapindex>` — deferred until approaching the 50,000 URL limit
- `<changefreq>` and `<priority>` tags — excluded per grilling decision (search engines ignore them)
- Static file generation — dynamic endpoint is sufficient for current scale
- Multiple sitemaps by year/category — not needed until URL count grows significantly
- Google Search Console / Bing Webmaster manual submission — operational concern, not code

## Further Notes

- The sitemap endpoint should reuse the existing `list_published_articles()` query to avoid drift between what the public blog shows and what search engines index
- `robots.txt` is a public endpoint with no auth requirement
- Both endpoints are read-only and idempotent — safe to call repeatedly by crawlers
- If `APP_BASE_URL` is misconfigured, sitemap URLs will be wrong — verify env in production
