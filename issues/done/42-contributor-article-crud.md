# Issue 42: Contributor Article CRUD (Backend + Frontend)

## Parent

Issue #38: Multi-author Support

## What to build

Enforce contributor permissions end-to-end: contributors can create and edit their own articles, but cannot publish, delete, or edit other users' articles. The backend returns 403 Forbidden for unauthorized actions. The frontend conditionally hides publish and delete buttons for contributors, and shows a clear indication when actions are unavailable.

## Acceptance criteria

- [x] `POST /api/admin/articles` accessible to contributors (creates article with their author_id)
- [x] `PUT /api/articles/{id}` for contributors: returns 403 if article is not owned by them
- [x] `PUT /api/articles/{id}` for contributors: returns 403 if payload attempts to set `status=published`
- [x] `DELETE /api/articles/{id}` returns 403 for contributors
- [x] Autosave endpoints accessible to contributors for their own articles only
- [x] All 403 responses include clear error message (e.g., "You do not have permission to perform this action")
- [ ] `AdminArticleEditView.vue` hides publish button for contributors
- [ ] `AdminArticleEditView.vue` hides delete button for contributors
- [ ] `AdminArticlesView.vue` hides delete buttons for contributors
- [ ] Contributor sees visual indication (tooltip or disabled state) when buttons are hidden
- [x] Integration tests verify contributor can create and edit own article
- [x] Integration tests verify contributor gets 403 on publish attempt
- [x] Integration tests verify contributor gets 403 on delete attempt
- [x] Integration tests verify contributor gets 403 when editing another user's article

## Implementation Notes

Backend implementation complete (2026-05-12):
- Added `check_article_permission` checks to `update_article_endpoint`, `delete_article_endpoint`, and `autosave_article_endpoint` in `app/routers/articles.py`
- Contributors get 403 on: editing others' articles, publishing any article, deleting any article, autosaving others' articles
- Added 11 integration tests in `tests/test_contributor_permissions.py`
- All 258 backend tests pass

Frontend items remain for follow-up issue.

## Blocked by

- Issue #39: Role Model Migration + Permission Service
- Issue #40: Article Ownership + Author Display
- Issue #41: Auth Me Endpoint + Frontend Role Store
