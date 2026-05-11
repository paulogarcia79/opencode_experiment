# 3. Per-Article Analytics Endpoint

## Parent

PRD: Article Performance Analytics (`prd/PRD-article-performance-analytics.md`)

## What to build

Create a new admin-only endpoint `GET /api/admin/articles/{id}/analytics` that returns detailed performance metrics for a single article, combining view counts from the `ArticleView` table with email engagement from `NewsletterSend` records.

## Acceptance criteria

- [ ] Endpoint `GET /api/admin/articles/{id}/analytics` returns JSON with: `total_views`, `unique_views_24h`, `email_sent`, `email_opens`, `email_clicks`, `email_open_rate`, `email_ctr`
- [ ] `total_views` counts all `ArticleView` records for the article
- [ ] `unique_views_24h` counts distinct `ip_hash` values within the last 24 hours
- [ ] Email metrics aggregated from `NewsletterSend` records for the article's `article_id`
- [ ] `email_open_rate` = (total_opens / email_sent) * 100, `email_ctr` = (total_clicks / email_sent) * 100
- [ ] Endpoint requires admin auth (`require_admin` dependency)
- [ ] Returns 404 for non-existent article IDs
- [ ] Backend tests cover: correct metrics returned, auth required, 404 for missing article

## Blocked by

- #1 ArticleView Model + View Tracking Service
