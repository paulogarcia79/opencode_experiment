# 4. Articles Performance List Endpoint

## Parent

PRD: Article Performance Analytics (`prd/PRD-article-performance-analytics.md`)

## What to build

Create an admin-only endpoint `GET /api/admin/articles/performance` that returns all articles with their view counts and email engagement metrics. This powers the "Views" and "Email CTR" columns in the admin articles list.

## Acceptance criteria

- [ ] Endpoint `GET /api/admin/articles/performance` returns a list of articles with: `id`, `title`, `slug`, `status`, `published_at`, `total_views`, `unique_views_24h`, `email_sent`, `email_opens`, `email_clicks`, `email_open_rate`, `email_ctr`
- [ ] Includes all articles (draft and published)
- [ ] Articles with no views return `0` for view metrics
- [ ] Articles with no newsletter sends return `0` for email metrics
- [ ] Endpoint requires admin auth (`require_admin` dependency)
- [ ] Backend tests cover: correct metrics for multiple articles, articles with no views, auth required

## Blocked by

- #1 ArticleView Model + View Tracking Service
