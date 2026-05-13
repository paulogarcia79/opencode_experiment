## Parent

PRD: `prd/PRD-role-based-dashboards.md`

## What to build

Build the contributor dashboard with a 3-per-row card grid showing only the contributor's own articles. Each card displays title, status badge, published date, and view count with Edit and Delete action buttons. Filter by status and search by title via URL query params with server-side filtering. Infinite scroll with 20 per fetch and "Load more" button. An attention badge on the page header shows the count of rejected articles (computed client-side). Rejected articles show a rejection feedback badge on their card. Write Vitest tests.

**End-to-end behavior**: A contributor logs in → sees a card grid of their articles at `/contributor`. Filters by status "draft" → only their drafts shown. Searches "hello" → only articles with "hello" in title. Sees a badge "2 need attention" at the top counting rejected articles. A rejected card shows a visible rejection indicator.

## Acceptance criteria

- [ ] `ContributorCardsView` renders at `/contributor` as the default child route
- [ ] Card grid: 3 cards per row (responsive, wraps to fewer on narrow screens)
- [ ] Each card: article title, status badge (colored per status: draft=slate, published=emerald, pending_review=accent red), published date (or "—"), view count, Edit and Delete buttons
- [ ] Edit button links to `/contributor/articles/{id}/edit`
- [ ] Delete button with confirmation, calls delete API
- [ ] Filter by status: dropdown or tabs with All, Drafts, Published, Pending Review options
- [ ] Search by title: text input, debounced, server-side filtering
- [ ] Filter and search state persisted in URL query params (`?status=draft&search=hello`)
- [ ] Infinite scroll: 20 per fetch, "Load more" button at bottom
- [ ] Attention badge: header shows count of articles needing attention (rejected articles, computed client-side from fetched data)
- [ ] Rejection feedback badge: visible on cards for articles that have been rejected (check latest ReviewAction)
- [ ] Loading, error, and empty states handled
- [ ] Frontend tests (Vitest): card grid renders contributor's articles, filter/search update URL and re-fetch, infinite scroll load-more, attention badge count, rejection badge on rejected cards, Edit/Delete buttons present

## Blocked by

- Issue 1 (Backend: Models, permissions, and API hardening)
- Issue 2 (Backend: Article list with sort, filter, and role scoping)
- Issue 4 (Frontend: Router, layout, and authentication)
