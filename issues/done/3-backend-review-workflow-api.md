## Parent

PRD: `prd/PRD-role-based-dashboards.md`

## What to build

Build the review workflow API endpoints on the backend. Contributors can submit articles for review. Editors/admins can approve or reject with feedback. A review queue endpoint returns all pending_review articles, and a count endpoint returns the pending count for the nav badge. All endpoints enforce role checks. Write pytest tests for the full review lifecycle.

**End-to-end behavior**: A contributor POSTs `submit-review` → article status becomes `pending_review` with `submitted_at` set. An editor GETs the review queue → sees the article. Editor POSTs `approve` → article published, `ReviewAction` created, `submitted_at` cleared. Or editor POSTs `reject` with feedback → article returns to draft, `ReviewAction` created with feedback stored.

## Acceptance criteria

- [ ] `POST /api/admin/articles/{id}/submit-review`: sets status to `pending_review`, sets `submitted_at = now`. Requires contributor, own article only
- [ ] `POST /api/admin/articles/{id}/approve`: sets status to `published`, clears `submitted_at`, creates `ReviewAction(action="approved")`. Requires admin or editor
- [ ] `POST /api/admin/articles/{id}/reject`: sets status to `draft`, clears `submitted_at`, creates `ReviewAction(action="rejected", feedback=body.feedback)`. Body includes `feedback` string. Requires admin or editor
- [ ] `GET /api/admin/articles/review`: returns all `pending_review` articles with author info and `submitted_at`. No pagination. Requires admin or editor
- [ ] `GET /api/admin/articles/review/count`: returns `{ pending_count: N }`. Requires admin or editor
- [ ] ReviewAction records preserve history: multiple rejections on same article create separate records
- [ ] Re-submission updates `submitted_at` to new timestamp
- [ ] Backend tests (pytest): full workflow (submit → approve, submit → reject, submit → reject → re-submit → approve), role enforcement (contributor can't approve, editor can't submit non-owned), ReviewAction record creation and retrieval

## Blocked by

- Issue 1 (Backend: Models, permissions, and API hardening)
