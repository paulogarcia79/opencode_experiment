# 6. Analytics Page — Article Performance Section

## Parent

PRD: Article Performance Analytics (`prd/PRD-article-performance-analytics.md`)

## What to build

Add an "Article Performance" section to the existing Analytics page (`AdminAnalyticsView.vue`). This section displays a table of articles sorted by views, showing detailed engagement metrics. It respects the existing 7d/30d/90d time range toggle for filtering view data.

## Acceptance criteria

- [ ] `AdminAnalyticsView.vue` includes a new "Article Performance" section below existing charts
- [ ] Table shows: article title, total views, unique views (24h), email sent, opens, clicks, open rate, CTR
- [ ] Articles sorted by total views (descending) by default
- [ ] Time range toggle (7d/30d/90d) filters view data by `viewed_at` date range
- [ ] Section styled consistently with existing analytics page (dark tech aesthetic, Chart.js theme)
- [ ] Loading state matches existing analytics page patterns
- [ ] Frontend tests verify section renders with correct data and time range filtering

## Blocked by

- #3 Per-Article Analytics Endpoint
