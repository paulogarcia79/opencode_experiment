## Parent

PRD: `prd/PRD-role-based-dashboards.md`

## What to build

Adapt the shared article editor component for all three roles. Contributors: replace the publish toggle with a "Submit for Review" button, show a read-only status badge, display rejection feedback as a banner, support "Update Review" button when pending_review, and "Re-submit for Review" when rejected. Auto-save forces `status: 'draft'` for contributors editing a pending_review article (frontend + backend defense). Autosave redirects to role-specific namespace URL. Admin/editor: publish toggle and newsletter remain functional. Admin: "Change Author" dropdown visible. Write Vitest tests.

**End-to-end behavior**: A contributor opens a draft → sees "Submit for Review" button instead of publish toggle. Clicks it → article status becomes pending_review. An editor rejects it with feedback → contributor re-opens article → sees rejection banner at top, "Re-submit for Review" button, read-only status showing "Rejected". Edit + auto-save → reverts to draft. Contributor re-submits → status back to pending_review.

## Acceptance criteria

- [ ] Contributor sees "Submit for Review" button (instead of publish toggle) in the toolbar area
- [ ] When article is `pending_review`, button changes to "Update Review"
- [ ] When article is `rejected`, button changes to "Re-submit for Review"
- [ ] Contributor sees a read-only status badge in the toolbar (shows current status: Draft / Pending Review / Rejected / Published)
- [ ] Rejected articles: rejection feedback banner at top of editor (latest ReviewAction with action="rejected")
- [ ] Contributor editing a `pending_review` article: auto-save sends `status: 'draft'` in payload; backend also forces draft
- [ ] Admin/editor: publish toggle and newsletter checkbox remain visible and functional
- [ ] Admin: "Change Author" dropdown remains visible in edit mode
- [ ] Autosave redirect path computed from `user.role`: contributor → `/contributor/articles/{id}/edit`, editor → `/editor/articles/{id}/edit`, admin → `/admin/articles/{id}/edit`
- [ ] Article editor routes registered under all three namespaces: `/admin/articles/new|:id/edit`, `/editor/articles/new|:id/edit`, `/contributor/articles/new|:id/edit`
- [ ] Frontend tests (Vitest): submit-for-review button renders for contributor, publish toggle hidden for contributor, read-only status badge shows correct status, rejection banner renders with feedback text, "Update Review" vs "Re-submit for Review" button states, autosave payload includes draft status for contributor, autosave redirect URL uses correct namespace

## Blocked by

- Issue 1 (Backend: Models, permissions, and API hardening)
- Issue 3 (Backend: Review workflow API)
- Issue 4 (Frontend: Router, layout, and authentication)
