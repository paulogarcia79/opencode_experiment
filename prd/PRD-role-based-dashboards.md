## Problem Statement

The blog application has three user roles — Admin, Editor, and Contributor — but after login, all users land on the same admin view and see the same navigation. A Contributor sees the full articles table with all articles and can navigate to Analytics, Tags, and Media Library, even though they can't meaningfully use those sections. The UI does not reflect the user's actual permissions.

Additionally, the articles table is cramped: eight columns squeezed into a constrained container with no text truncation, no horizontal scroll, and a slug column that's nearly invisible against the dark background. Contributors lack a way to submit articles for editorial review before publication.

## Solution

Three separate dashboard namespaces — `/admin`, `/editor`, `/contributor` — each with role-scoped navigation, landing pages, and features. A single login page redirects users to their appropriate dashboard based on role. The articles table is redesigned with expandable rows, infinite scroll, filter tabs, and sortable columns. A new review workflow lets contributors submit articles for editorial approval, and editors/admins can approve or reject with feedback.

## User Stories

### Authentication & Routing
1. As any user, I want to log in from a single login page, so that I don't need to know which URL to visit
2. As any user, I want to be redirected to my role's dashboard after login, so that I land on the right starting page
3. As an admin, I want to access all `/admin/*` routes, so that I can manage the entire platform
4. As an editor, I want to be blocked from `/admin/*` routes with a clear forbidden message, so that I understand my access boundaries
5. As a contributor, I want to be blocked from `/admin/*` and `/editor/*` routes with a forbidden message, so that I understand my access boundaries
6. As any user visiting a forbidden route, I want to see a 403 page with a link back to my dashboard, so that I can recover from navigation mistakes

### Navigation & Layout
7. As an admin, I want navigation links for Articles, Import, Media, Tags, Analytics, Settings, and Users, so that I can access all management features
8. As an editor, I want navigation links for Articles, Import, and Settings, so that I can manage content without distracting sections I don't use
9. As a contributor, I want navigation links for Articles (my articles), Import, and Settings, so that I can manage my own content
10. As an editor/admin, I want a Review tab with a badge showing pending count, so that I know when there are submissions to review
11. As any user, I want a consistent top navigation bar across all dashboards, so that the experience feels unified

### Admin Articles Table
12. As an admin, I want to see all articles in an expandable table, so that I can browse the full catalog
13. As an admin/editor, I want to click anywhere on a table row to expand it, so that I can quickly see article details
14. As an admin/editor, I want to expand multiple rows simultaneously, so that I can compare article details side by side
15. As an admin/editor, I want expanded rows to show a detail card with Published date, Views, and Email CTR, so that I can inspect key metrics at a glance
16. As an admin/editor, I want the slug column removed from the table, so that irrelevant or hard-to-read data doesn't clutter the view
17. As an admin/editor, I want filter tabs (All, Drafts, Published, Pending Review) above the table, so that I can focus on articles by status
18. As an admin/editor, I want filter state persisted in the URL query string, so that I can share or bookmark filtered views
19. As an admin/editor, I want to sort articles by clicking column headers (Title, Author, Status, Published date, Created, Last Modified), so that I can order the table as needed
20. As an admin/editor, I want infinite scroll with 20 articles per fetch and a "Load more" button, so that the table performs well with many articles
21. As an admin, I want to see Edit and Delete buttons on all articles in the table, so that I can manage any article
22. As an editor, I want to see Edit and Delete buttons on all articles in the table, so that I can manage any article

### Contributor Dashboard
23. As a contributor, I want to see my articles in a card grid (3 per row), so that I can focus on my own work
24. As a contributor, I want each card to show the article title, status badge, published date, and view count, so that I can assess each article at a glance
25. As a contributor, I want Edit and Delete buttons on my article cards, so that I can manage my own articles
26. As a contributor, I want to filter my articles by status and search by title, so that I can find specific articles quickly
27. As a contributor, I want filter and search state persisted in the URL query string, so that I can share or bookmark filtered views
28. As a contributor, I want infinite scroll with 20 articles per fetch and a "Load more" button, so that the view performs well with many articles
29. As a contributor, I want a badge count showing how many of my articles are rejected or need attention, so that I can prioritize revisions
30. As a contributor, I want to see a rejection feedback badge on rejected article cards, so that I know which articles were returned for revision

### Review Workflow — Contributor
31. As a contributor, I want a "Submit for Review" button in the article editor instead of a publish toggle, so that I can send articles for editorial approval
32. As a contributor, I want to see a read-only status badge in the editor toolbar, so that I know which state my article is in
33. As a contributor submitting for review, I want the article status to change to "pending_review" and the submitted timestamp to be recorded, so that editors can see when it was submitted
34. As a contributor editing an article that's pending review, I want auto-save to revert it to draft, so that the review is effectively restarted
35. As a contributor, I want a "Update Review" button (visible only when the status is pending_review) to resubmit after making edits
36. As a contributor, I want a "Re-submit for Review" button (visible only after rejection) so that I can send my article back after addressing feedback
37. As a contributor, I want to see rejection feedback as a banner at the top of the article editor, so that I know what to fix

### Review Workflow — Editor/Admin
38. As an editor/admin, I want a Review Queue page listing all pending_review articles, so that I can triage submissions
39. As an editor/admin, I want the review queue table to show article title, author, submitted date, and Approve/Reject buttons, so that I can act quickly
40. As an editor/admin, I want to see article description and any previous rejection feedback when expanding a review row, so that I have full context before deciding
41. As an editor/admin, I want a link from each review row to open the article in the full editor, so that I can do a thorough review
42. As an editor/admin, I want to click "Approve" and see a confirmation dialog showing article title, author, and submitted date, so that I don't accidentally approve the wrong article
43. As an editor/admin, I want approving an article to immediately publish it and create an approval record, so that the workflow is efficient
44. As an editor/admin, I want to click "Reject" and provide feedback in a modal, so that the contributor knows why
45. As an editor/admin, I want rejecting an article to set it back to draft and create a rejection record with feedback, so that the contributor can revise
46. As an editor/admin, I want to see a pending review count badge on the Review nav tab, so that I know when there are new submissions
47. As an editor/admin, I want to see all previous rejection feedback on an article that has been rejected before, so that I can understand the article's history

### Article Editor Role Adaptations
48. As a contributor, I should never see a publish toggle in the editor, so that I don't attempt unauthorized actions
49. As an admin/editor, I want the publish toggle and newsletter checkbox visible in the editor, so that I can publish and notify subscribers
50. As an admin/editor editing a non-owned article, I want to still be able to publish and edit, so that I can manage all content
51. As any user with an article in the editor, I want auto-save to redirect to my own namespace URL (e.g., `/contributor/articles/{id}/edit`), so that links stay within my dashboard
52. As an admin, I want the "Change Author" dropdown visible in the editor, so that I can reassign articles

### Backend Authorization
53. As a contributor requesting another user's article via the API, I want to receive a 404 instead of a 403, so that I cannot probe for article existence
54. As an admin, I want analytics endpoints restricted to admin only, so that sensitive data is protected
55. As an admin, I want newsletter blast status restricted to admin only, so that operational data is protected
56. As an admin, I want article performance endpoints restricted to admin only, so that detailed metrics are protected
57. As a contributor, I want to be able to delete my own articles, so that I can clean up unwanted drafts

### Public API Boundaries
58. As a public visitor, I want only published articles to appear in the public API, so that drafts and pending reviews are never exposed

## Implementation Decisions

### Architecture
- Three separate URL namespaces: `/admin`, `/editor`, `/contributor` — each with its own Vue Router tree
- A single `DashboardLayout` base component with a top navigation bar and a nav slot; each role has a thin wrapper (`AdminDashboard`, `EditorDashboard`, `ContributorDashboard`) that fills the slot with role-specific links
- The existing `AdminArticleEditView` component is reused across all three namespaces, adapting its behavior based on the current user's role from the Pinia store
- A single login page at `/admin/login`; on success, the login component redirects to the appropriate dashboard based on `user.role`
- A single `/forbidden` route that reads the user's role from the store and generates the correct "back to dashboard" link
- Route guards per namespace: `/admin/*` requires `role === 'admin'`, `/editor/*` requires `admin` or `editor`, `/contributor/*` requires any authenticated user. Violations redirect to `/forbidden`
- Cross-namespace editor redirect: if an editor visits `/contributor/articles/{id}/edit`, they are redirected to `/editor/articles/{id}/edit` (same article, their namespace)

### Articles Table Redesign
- A reusable `ExpandableTable` component: click anywhere on a row to expand; supports multiple simultaneously expanded rows; expanded state shows a sub-row with a styled detail card (distinct background) containing Published date, Views, and Email CTR
- The slug column is removed entirely
- Filter tabs above the table: All, Drafts, Published, Pending Review — filter state persisted in URL query params (`?status=published`)
- Sortable columns: clicking a column header sends `?sort=column&order=asc|desc` to the backend; backend performs `ORDER BY`
- Infinite scroll: 20 items per fetch using existing `skip`/`limit` params; a "Load more" button appears at the bottom when more items are available

### Contributor Card Grid
- Cards displayed 3 per row in a responsive grid
- Each card shows: title, status badge, published date, view count, Edit and Delete action buttons
- Filter by status and search by title, both as URL query params backed by server-side filtering
- Attention badge: counts rejected articles client-side by iterating over fetched articles with status `draft` that have a recent rejection `ReviewAction`
- Rejection feedback badge on the card itself (visible when article has been rejected)

### Review Workflow
- New article status: `pending_review` (in addition to existing `draft` and `published`)

#### Article Model Changes
- `status` field extended to accept `"pending_review"` as a valid value
- New `submitted_at` datetime field (nullable) — set when contributor submits, cleared on approve or reject

#### ReviewAction Model
- New SQLModel table: `id` (UUID PK), `article_id` (FK), `reviewer_id` (FK to User), `action` (enum: `approved` | `rejected`), `feedback` (text, nullable), `created_at` (timestamp)

#### New API Endpoints
- `POST /api/admin/articles/{id}/submit-review` — sets status to `pending_review`, sets `submitted_at = now`. Requires contributor role, own article only
- `POST /api/admin/articles/{id}/approve` — sets status to `published`, clears `submitted_at`, creates `ReviewAction(action="approved")`. Requires admin or editor
- `POST /api/admin/articles/{id}/reject` — sets status to `draft`, clears `submitted_at`, creates `ReviewAction(action="rejected", feedback=body.feedback)`. Body includes `feedback` string. Requires admin or editor
- `GET /api/admin/articles/review` — returns all `pending_review` articles (no pagination). Requires admin or editor
- `GET /api/admin/articles/review/count` — returns `{ pending_count: N }`. Requires admin or editor

#### Review Queue Page
- Rendered under both `/admin/review` and `/editor/review` (duplicate routes, same shared component)
- Table columns: Title, Author, Submitted Date, Approve/Reject buttons
- Expand row: shows article description and previous rejection feedback (latest ReviewAction where action is "rejected")
- "Approve" button opens a confirmation dialog showing article title, author, submitted date, with Approve/Cancel buttons
- "Reject" button opens a feedback modal with a text area; on submit, sends reject with feedback
- A link in each row opens the article in the full editor for detailed review

### Article Editor Role Adaptations
- Contributors: the publish toggle is replaced by a "Submit for Review" button; a read-only status badge appears in the same toolbar area showing the current status
- When the article is `pending_review`, the button changes to "Update Review"
- When rejected, the button changes to "Re-submit for Review" and a rejection feedback banner appears at the top of the editor
- Contributors editing a `pending_review` article: auto-save forces `status: 'draft'` in the payload (frontend) and the backend also enforces it (defense in depth)
- Admin/editor: publish toggle and newsletter checkbox remain visible and functional
- Admin: "Change Author" dropdown remains visible
- Autosave redirect path is computed from `user.role` instead of being hardcoded to `/admin/`

### Backend Hardening
- `GET /api/admin/articles` and `GET /api/admin/articles/{id}`: contributors auto-filtered to `WHERE author_id = current_user.id`. If a contributor requests another's article by ID, return 404
- All analytics endpoints: role requirement tightened to `["admin"]` only
- Newsletter blast status endpoint: role requirement tightened to `["admin"]` only
- Article performance endpoints: role requirement tightened to `["admin"]` only
- Permission service: contributor permission set updated to include `delete`
- Article list endpoint gets new query params: `sort` (column name), `order` (`asc`|`desc`), `status` filter

### Frontend Permissions Composable
- `useArticlePermissions` updated: contributors gain `delete` permission; admin gains `reassign` permission

### Public API
- `GET /api/articles` and `GET /api/articles/{slug}`: return only articles where `status = 'published'`. Articles with `draft` or `pending_review` status are excluded

## Testing Decisions

### What Makes a Good Test
- Test external behavior, not implementation details (e.g., test that a button is rendered/hidden for a role, not how the computed property is structured)
- Backend: test API responses and status codes for each role against each endpoint
- Frontend: test component rendering with mocked stores to simulate different roles
- Review workflow: test status transitions and that `ReviewAction` records are created correctly

### Backend Tests (pytest + SQLite in-memory)
- Article model: test `pending_review` status and `submitted_at` field
- ReviewAction model: test creation, FK relationships, cascade behavior
- Article endpoint scoping: test contributors only see their own articles, get 404 for others'
- Review workflow endpoints: test submit-review, approve, reject for each role
- Endpoint tightening: test editors/contributors get 403 from analytics, newsletter, performance endpoints
- Contributor delete: test contributors can delete own articles
- Sort/filter params: test `?sort=updated_at&order=desc` and `?status=published` produce correct results
- Public API: test only published articles appear
- Review count endpoint: test correct count returned

### Frontend Tests (Vitest + @vue/test-utils)
- DashboardLayout: test nav items rendered per role
- ExpandableTable: test expand/collapse behavior, multi-expand, sub-row content rendering
- AdminArticlesView: test filter tabs, sort clicks, infinite scroll load-more, expanded detail card
- EditorArticlesView: test same structure as admin but within editor namespace
- ContributorCardsView: test card grid rendering, filter/search params, attention badge count, rejection feedback badge
- ReviewQueue page: test table rendering, approve confirmation dialog, reject feedback modal, expand row shows feedback history
- ArticleEditor adaptations: test submit-for-review button (contributor), publish toggle (admin/editor), read-only status badge, rejection feedback banner, autosave reverts pending_review to draft
- Forbidden page: test 403 message and correct dashboard link per role
- Login redirect: test routing based on role after successful login
- Router guards: test each namespace blocks incorrect roles and redirects to forbidden
- Cross-namespace editor redirect: test editor visiting `/contributor/articles/:id/edit` redirects to `/editor/articles/:id/edit`
- useArticlePermissions composable: test all role/ownership combinations including new `delete` for contributors and `reassign` for admin

### Prior Art
- Backend tests follow pattern from `tests/` directory using FastAPI `TestClient` and SQLite in-memory
- Frontend tests follow pattern from `frontend/src/views/__tests__/` and `frontend/src/composables/__tests__/`
- Existing `PRD-role-aware-article-ui.md` tests for the `useArticlePermissions` composable serve as reference

## Out of Scope

- Email notifications for review workflow (no Resend integration)
- Role-based analytics or dashboard metrics specific to each role
- OAuth account settings changes (existing functionality unchanged)
- Tag management for editors (existing access unchanged per user decision)
- Media library for editors (existing access unchanged per user decision)
- Slug generation changes (slugs continue to generate on article creation only)
- Any changes to subscriber management or newsletter sending flow
- Role hierarchy changes (three roles remain: admin, editor, contributor)

## Further Notes

- The `pending_review` status badge uses the accent color (`#F43F5E`) from the design system
- The ReviewAction table tracks review history; old feedback is preserved when a contributor re-submits, so editors can see the full rejection history
- The `submitted_at` field is set on submission, updated on re-submission, and cleared on approval or rejection
- The separate review queue page loads all pending_review articles at once (no pagination) since the set is expected to be small
- Backend-driven sorting is used because client-side sorting is incompatible with server-side infinite scroll pagination
- The existing `require_role` dependency pattern is followed for all new endpoints
