# PRD: Article Performance Analytics

## Problem Statement

As a blog administrator, I have no visibility into which articles are performing well. I can see aggregate newsletter metrics (total opens, clicks, open rate) on the Analytics page, but I cannot tell which specific articles drove that engagement. I also have no idea how many people are reading articles directly on the site. This makes it impossible to understand content performance, identify popular topics, or make data-driven decisions about what to write next.

## Solution

Implement **Article Performance Analytics** that tracks page views and exposes per-article email engagement metrics. This adds a new `ArticleView` table for deduplicated view tracking, two new admin API endpoints for article-level analytics, and extends the existing admin UI with view columns in the articles list and a performance section on the Analytics page.

## User Stories

1. As an admin, I want to see how many views each article has in the articles list, so I can quickly identify my most popular content.
2. As an admin, I want to see the email open rate and CTR for each article in the articles list, so I can compare newsletter performance across articles at a glance.
3. As an admin, I want to view detailed performance metrics for a specific article (total views, unique views in 24h, email sent, opens, clicks, open rate, CTR), so I can understand the full engagement picture for that article.
4. As an admin, I want to see article performance data on the Analytics page, so I can correlate article performance with subscriber growth trends.
5. As a reader, I want my page view to be counted when I visit an article, so that the analytics reflect real readership.
6. As an admin, I want views from the same IP within 24 hours to be deduplicated, so that refresh spam doesn't inflate the numbers.
7. As an admin, I want to sort articles by views or engagement in the articles list, so I can quickly find top performers.
8. As an admin, I want the view tracking to be automatic (no extra frontend code needed), so that existing article pages start collecting data immediately.

## Implementation Decisions

### 1. ArticleView Model

- **New table**: `article_views` with fields: `id` (UUID), `article_id` (FK to articles), `ip_hash` (SHA-256 hash of IP address), `viewed_at` (timestamp).
- **No IP addresses stored** — only a SHA-256 hash for privacy.
- **Deduplication**: 24-hour window per IP hash per article. A view is only recorded if no existing view from the same IP hash exists within the last 24 hours.

### 2. View Tracking Service

- **New service**: `view_tracking_service.py` with a `record_view(session, article_id, ip_address)` function.
- **Logic**: Hash the IP, check for existing views within 24 hours, insert if none found.
- **Caller responsibility**: The service adds the record to the session but does NOT commit. The caller (router) decides when to commit.

### 3. Automatic View Recording

- **Modified endpoint**: `GET /api/articles/{slug}` calls `record_view()` before returning the article.
- **IP source**: For now, uses a hardcoded `127.0.0.1` (since Nginx is the entry point in production). Future: extract from `X-Forwarded-For` or `X-Real-IP` headers.
- **Draft articles**: No view is recorded for draft articles (404 response).

### 4. Per-Article Analytics Endpoint

- **New endpoint**: `GET /api/admin/articles/{id}/analytics` (admin-only).
- **Returns**: `total_views`, `unique_views_24h`, `email_sent`, `email_opens`, `email_clicks`, `email_open_rate`, `email_ctr`.
- **Email metrics**: Aggregated from `NewsletterSend` records for the given `article_id` (sum of `open_count`, `click_count`, count of `status='sent'`).

### 5. Articles Performance List Endpoint

- **New endpoint**: `GET /api/admin/articles/performance` (admin-only).
- **Returns**: List of all articles with their view counts and email metrics. Suitable for populating the articles table columns.

### 6. Admin Articles List UI

- **Modified**: `AdminArticlesView.vue` adds "Views" and "Email CTR" columns to the articles table.
- **Data source**: Fetches from the new performance list endpoint, or enriches the existing articles list response.

### 7. Analytics Page UI

- **Modified**: `AdminAnalyticsView.vue` adds an "Article Performance" section below the existing charts.
- **Content**: A table of articles sorted by views, showing title, total views, unique views (24h), email sent, opens, clicks, open rate, CTR.
- **Time range**: Respects the existing 7d/30d/90d toggle for filtering views by date range.

### 8. Router Registration

- **New router**: `article_analytics_router` registered in `app/main.py` alongside the existing `analytics.router`.
- **Prefix**: `/api/admin/articles/{article_id}/analytics`

### 9. Model Registration

- **`ArticleView`** added to `app/models/__init__.py` so it's included in table creation and Alembic migrations.

## Testing Decisions

- **Backend**: Integration tests following the existing pattern in `tests/test_articles.py` and `tests/test_analytics.py`.
  - Test that `GET /api/articles/{slug}` records a view for published articles.
  - Test that duplicate views from the same IP within 24 hours are not recorded.
  - Test that views after 24 hours are recorded.
  - Test that different IPs both record views.
  - Test that draft articles do not record views.
  - Test the per-article analytics endpoint returns correct view and email metrics.
  - Test the per-article analytics endpoint requires admin auth.
  - Test the per-article analytics endpoint returns 404 for non-existent articles.
- **Prior art**: `tests/test_analytics.py` for analytics endpoint testing, `tests/test_articles.py` for article endpoint testing, `tests/test_webhooks.py` for deduplication patterns.
- **Frontend**: Unit tests for the updated `AdminArticlesView.vue` and `AdminAnalyticsView.vue` to verify new columns and data rendering.

## Out of Scope

- Unique visitor tracking via cookies or session IDs.
- Referrer / traffic source tracking (UTM parameter parsing).
- Reading time / scroll depth tracking.
- Per-link click tracking within emails.
- Article performance time-series charts (views over time per article).
- Popular articles widget on the public site.
- Geographic / device breakdown of readers.

## Further Notes

- The existing `NewsletterSend` model already tracks `open_count` and `click_count` per recipient. This PR leverages that data — no changes to email tracking are needed.
- The `EmailEvent` table stores raw webhook payloads but is not queried for analytics. This PR does not change that.
- View tracking is intentionally simple: IP hash + 24-hour dedup. This will count some bot traffic, but that's acceptable for v1.
- The IP address is currently hardcoded to `127.0.0.1` because the app runs behind Nginx. In production, the real IP should be extracted from `X-Forwarded-For` or `X-Real-IP` headers — this is a follow-up item.
