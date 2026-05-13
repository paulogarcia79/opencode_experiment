## Parent

PRD: `prd/PRD-role-based-dashboards.md`

## What to build

Build the backend foundation for role-based dashboards: extend the Article model with `pending_review` status and `submitted_at` field, create the `ReviewAction` model, update the permission service to give contributors `delete`, tighten analytics/newsletter/performance endpoints to admin-only, and enforce public API to only return published articles. Write comprehensive pytest tests for all changes.

**End-to-end behavior**: An admin can call analytics endpoints; an editor gets 403. A contributor can delete their own article but gets 404 when requesting another's article by ID. The public API never returns drafts or pending_review articles. The `ReviewAction` table exists and accepts `approved`/`rejected` records.

## Acceptance criteria

- [ ] Article model: `status` field accepts `"pending_review"` value; `submitted_at` datetime field added (nullable)
- [ ] ReviewAction model: SQLModel table with `id` (UUID PK), `article_id` (FK), `reviewer_id` (FK to User), `action` (enum: approved/rejected), `feedback` (text, nullable), `created_at` (timestamp)
- [ ] Permission service: contributor set updated to include `delete`
- [ ] All analytics endpoints require `["admin"]` only
- [ ] Newsletter blast status endpoint requires `["admin"]` only
- [ ] Article performance endpoints require `["admin"]` only
- [ ] Public API (`GET /api/articles`, `GET /api/articles/{slug}`): only published articles returned
- [ ] Alembic migration generated for Article + ReviewAction changes
- [ ] Backend tests (pytest): Article model status/submitted_at, ReviewAction model CRUD, contributor delete permission, endpoint tightening (403 for wrong role), public API filtering

## Blocked by

None - can start immediately
