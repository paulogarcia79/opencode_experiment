# 5. Admin Articles List — View Columns

## Parent

PRD: Article Performance Analytics (`prd/PRD-article-performance-analytics.md`)

## What to build

Add "Views" and "Email CTR" columns to the admin articles list table (`AdminArticlesView.vue`). The data comes from the new performance list endpoint, giving administrators instant visibility into article performance without leaving the articles page.

## Acceptance criteria

- [ ] `AdminArticlesView.vue` displays "Views" column showing `total_views` per article
- [ ] `AdminArticlesView.vue` displays "Email CTR" column showing `email_ctr` percentage
- [ ] Data fetched from `GET /api/admin/articles/performance` endpoint
- [ ] Columns styled consistently with existing table design (dark tech aesthetic)
- [ ] Articles with zero views/CTR display "0" not empty
- [ ] Frontend tests verify columns render with correct data

## Blocked by

- #4 Articles Performance List Endpoint
