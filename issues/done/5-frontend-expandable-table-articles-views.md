## Parent

PRD: `prd/PRD-role-based-dashboards.md`

## What to build

Build the reusable `ExpandableTable` component and use it to redesign the admin and editor articles views. The table supports click-anywhere-to-expand, multi-expand, sub-row detail cards, filter tabs with URL params, sortable column headers, infinite scroll (20/page with "Load more" button), and the slug column removed. Create `AdminArticlesView` and `EditorArticlesView` using this component with appropriate edit/delete permissions. Write Vitest tests.

**End-to-end behavior**: An admin loads `/admin` → sees expandable table of all articles. Clicks a row → sub-row reveals a detail card with Published date, Views, CTR. Clicks "Drafts" filter tab → URL updates to `?status=draft`, only drafts shown. Clicks "Title" header → table sorts by title, URL gets `?sort=title&order=asc`. Scrolls to bottom → "Load more" button appears, fetches next 20. Editor gets same experience at `/editor`.

## Acceptance criteria

- [ ] `ExpandableTable` reusable component: emits expand/collapse, supports `expandedIds` prop for multi-expand, slot for expanded row content
- [ ] Click anywhere on a row expands/collapses it. Multiple rows can be expanded simultaneously
- [ ] Expanded sub-row: styled detail card with distinct background showing Published date, Views, and Email CTR (labeled fields)
- [ ] Slug column removed from table entirely
- [ ] Filter tabs above table: All, Drafts, Published, Pending Review
- [ ] Filter state persisted in URL query params (`?status=published`). Changing filter fetches filtered results from backend
- [ ] Sortable columns: clicking Title, Author, Status, Published date headers toggles sort (`?sort=column&order=asc|desc`). Ascending indicator on active sort column
- [ ] Infinite scroll: 20 items per fetch using backend `skip`/`limit` params
- [ ] "Load more" button appears at bottom when more items available (not auto-trigger on scroll)
- [ ] `AdminArticlesView`: all articles, Edit/Delete buttons on every row (admin permissions)
- [ ] `EditorArticlesView`: all articles, Edit/Delete buttons on every row (editor permissions)
- [ ] Existing article actions preserved: Edit links to editor under correct namespace, Delete with confirmation
- [ ] Loading state, error state, empty state handled
- [ ] Frontend tests (Vitest): expand/collapse, multi-expand renders multiple sub-rows, detail card content, filter tabs update URL and re-fetch, sort click sends correct params, load-more button fetches next page, Edit/Delete buttons visible per role

## Blocked by

- Issue 1 (Backend: Models, permissions, and API hardening)
- Issue 2 (Backend: Article list with sort, filter, and role scoping)
- Issue 4 (Frontend: Router, layout, and authentication)
