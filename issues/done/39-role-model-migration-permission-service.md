# Issue 39: Role Model Migration + Permission Service

## Parent

Issue #38: Multi-author Support

## What to build

Foundation for the entire multi-author system. Replace `is_admin: bool` on the `User` model with a `role: str` enum (`admin`, `editor`, `contributor`), add `is_active: bool` for soft deactivation, create an Alembic migration that migrates existing users, and extract a `permission_service.py` deep module that encapsulates all role-based permission checks. Replace the `require_admin` dependency with a new `require_role(allowed_roles)` dependency that checks JWT validity, user verification, active status, and role membership.

## Acceptance criteria

- [ ] `User` model has `role: str` field (default `"contributor"`) instead of `is_admin: bool`
- [ ] `User` model has `is_active: bool` field (default `True`)
- [ ] Alembic migration correctly migrates `is_admin=True` → `role=admin`, `is_admin=False` → `role=contributor`, then drops `is_admin` column
- [ ] `app/services/permission_service.py` exists with `check_article_permission(user, article, action) -> bool` interface
- [ ] `app/dependencies.py` has `require_role(allowed_roles: list[str])` that replaces `require_admin`
- [ ] `require_role` checks: JWT valid, token version matches, user exists, user is verified, user is active, user role is in allowed_roles
- [ ] All existing admin article endpoints updated to use `require_role(["admin", "editor", "contributor"])` or appropriate role lists
- [ ] Permission service unit tests cover all role × action combinations (admin/editor/contributor × create/edit own/edit others/delete/publish)
- [ ] Existing tests pass with the new dependency (backward compatible for existing admin user)

## Blocked by

None - can start immediately
