## Parent

PRD: `prd/PRD-role-based-dashboards.md`

## What to build

Build the Review Queue page (shared under `/admin/review` and `/editor/review`) showing all `pending_review` articles in a table. Each row shows Title, Author, Submitted Date, Approve/Reject buttons. Expanding a row reveals article description and previous rejection feedback. "Approve" opens a confirmation dialog with article context. "Reject" opens a feedback modal. Approve/reject actions call the review workflow API. Also update the `useArticlePermissions` composable: add `delete` for contributors, add `reassign` for admin. Wire the review count badge into the nav. Write Vitest tests.

**End-to-end behavior**: An editor navigates to `/editor/review` → sees a table of pending_review articles with a count badge in the nav. Clicks "Approve" on an article → confirmation dialog shows title, author, submitted date → confirms → article published, disappears from queue. Clicks "Reject" on another → modal opens → types feedback → submits → article returns to draft, `ReviewAction` created.

## Acceptance criteria

- [ ] `ReviewQueue` page component registered at both `/admin/review` and `/editor/review`
- [ ] Table columns: Title, Author, Submitted Date, Approve / Reject action buttons
- [ ] Expand row: shows article description and previous rejection feedback (latest ReviewAction with action="rejected", rendered as labeled text)
- [ ] "Approve" button: opens confirmation dialog showing article title, author, submitted date. Approve/Cancel buttons
- [ ] Confirm approve → calls `POST /api/admin/articles/{id}/approve` → article removed from queue on success
- [ ] "Reject" button: opens modal with textarea for feedback. Submit/Cancel buttons
- [ ] Confirm reject → calls `POST /api/admin/articles/{id}/reject` with feedback body → article removed from queue on success
- [ ] Each row has a link to open the article in the full editor for detailed review (links to `/admin/articles/{id}/edit` or `/editor/articles/{id}/edit` depending on namespace)
- [ ] Review count badge in nav: fetches `GET /api/admin/articles/review/count`, displays count on Review tab
- [ ] `useArticlePermissions` composable: contributor gets `delete` in permission set; admin gets `reassign` in permission set
- [ ] All existing `useArticlePermissions` tests updated for new permissions
- [ ] Frontend tests (Vitest): review queue renders pending articles, expand row shows description and feedback, approve dialog content and confirm action, reject modal feedback submission, approve/reject remove article from list, count badge fetches and renders, composable permissions for contributor delete and admin reassign

## Blocked by

- Issue 1 (Backend: Models, permissions, and API hardening)
- Issue 3 (Backend: Review workflow API)
- Issue 4 (Frontend: Router, layout, and authentication)
- Issue 5 (Frontend: ExpandableTable + admin/editor articles views)
