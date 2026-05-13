## Problem Statement

As the blog grows, I need to collaborate with other writers and editors, but the current system only supports a single admin user with a boolean `is_admin` flag. I can't invite team members, assign different permission levels, track who wrote or edited what, or manage contributor workflows. This limits the platform to solo use and prevents scaling to a multi-author publication.

## Solution

Implement a role-based multi-author system that replaces the `is_admin` boolean with a proper role enum (`admin`, `editor`, `contributor`), adds article ownership tracking, enforces role-based permissions on all article endpoints, and provides an admin UI for managing users and their roles.

## User Stories

1. As an **admin**, I want to invite new users via email so that they can join the platform as team members.
2. As an **admin**, I want to assign roles (admin, editor, contributor) to users so that they have appropriate access levels.
3. As an **admin**, I want to change a user's role at any time so that I can adjust permissions as team needs evolve.
4. As an **admin**, I want to deactivate a user's account so that they can no longer access the system, while preserving their existing articles.
5. As an **admin**, I want to reassign an article from one user to another so that content ownership can be transferred when someone leaves the team.
6. As an **admin**, I want to see a list of all users with their email, role, and status so that I can manage the team at a glance.
7. As an **editor**, I want to create, edit, and publish any article so that I can manage content across the publication.
8. As an **editor**, I want to delete articles so that I can remove outdated or incorrect content.
9. As an **editor**, I want to manage tags and import content so that I can organize and onboard articles.
10. As a **contributor**, I want to create and edit my own articles so that I can write content for the publication.
11. As a **contributor**, I want my articles to remain in draft status until an editor or admin publishes them so that content goes through a review process.
12. As a **contributor**, I want to see a clear indication when I cannot publish or delete an article so that I understand my permission boundaries.
13. As a **contributor**, I want to be prevented from editing another user's articles so that content ownership is respected.
14. As any **authenticated user**, I want to see the author name on articles in the admin list so that I know who wrote or owns each piece.
15. As any **authenticated user**, I want to see who made each revision in the revision history panel so that I can track content changes by author.
16. As a **new user**, I want to receive an email with a setup link so that I can create my password and activate my account.
17. As a **deactivated user**, I want my existing articles to remain published on the public site so that readers can still access the content I wrote.
18. As a **deactivated user**, I want to be unable to log in so that my access is properly revoked.

## Implementation Decisions

### Role System
- Replace `is_admin: bool` on `User` model with `role: str` enum field (`admin`, `editor`, `contributor`)
- Add `is_active: bool = True` field to `User` model for soft deactivation
- Migration: `is_admin=True` → `role=admin`, `is_admin=False` → `role=contributor`, then drop `is_admin` column

### Article Ownership
- Add `author_id: uuid.UUID` foreign key to `Article` model referencing `User.id`
- Add `author` relationship on `Article` for eager loading author details
- On article creation, set `author_id` to the current authenticated user's ID
- Existing articles (pre-migration) will have `author_id` set to the first admin user or nullable with backfill

### Permission Enforcement
- Replace `require_admin` dependency with `require_role(allowed_roles: list[str])` that checks:
  - JWT validity and token version
  - User exists and is verified
  - User `is_active` is True
  - User `role` is in `allowed_roles`
- Article endpoint permissions:
  - `POST /api/admin/articles` — `contributor`, `editor`, `admin`
  - `PUT /api/articles/{id}` — `contributor` (own only), `editor`, `admin`
  - `DELETE /api/articles/{id}` — `editor`, `admin`
  - `PUT /api/articles/{id}` with `status=published` — `editor`, `admin` only
  - All other admin endpoints — `editor`, `admin`
- Contributors attempting to edit another user's article receive 403 Forbidden
- Contributors attempting to publish receive 403 Forbidden

### Revision History
- Add `author_id: uuid.UUID` (nullable) to `ArticleRevision` model
- On explicit save/publish, capture current user's ID in revision
- Auto-save revisions continue to exclude author (as current behavior)
- Revision panel displays author email next to timestamp

### User Management API
- New router `app/routers/users.py` with:
  - `GET /api/admin/users` — List all users (admin only)
  - `POST /api/admin/users/invite` — Invite user via email (admin only)
  - `PUT /api/admin/users/{id}/role` — Change user role (admin only)
  - `PUT /api/admin/users/{id}/active` — Toggle user active status (admin only)
- Invite flow: generate temporary token, email setup link, user sets password, auto-verified

### Auth API Changes
- New endpoint `GET /api/auth/me` — Returns current user profile (email, role, is_active, is_verified)
- Login response unchanged (returns JWT token)
- Frontend calls `/api/auth/me` after login to populate user profile in Pinia store

### Article Reassignment
- New endpoint `PUT /api/admin/articles/{id}/reassign` — Change article author (editor, admin only)
- Creates revision with `change_type="reassign"` capturing old and new author
- Dropdown in article edit view (visible to editors/admins) lists all active users

### Frontend Changes
- Pinia `admin` store extended to store user profile (email, role, is_active) alongside token
- Router guards check role before allowing access to admin pages
- UI elements conditionally shown/hidden based on role:
  - Publish button hidden for contributors
  - Delete button hidden for contributors
  - "Change Author" dropdown visible only to editors/admins
  - User management page visible only to admins
- New admin views:
  - `AdminUsersView.vue` — User list, invite, role management, deactivation
- Article list views display author name/email

### Schema Changes
- `ArticleCreate` extended with optional `author_id` (backend sets automatically from authenticated user)
- `UserRead` schema: `id`, `email`, `role`, `is_active`, `is_verified`, `created_at`
- `UserInvite` schema: `email`, `role`
- `UserRoleUpdate` schema: `role`
- `UserActiveUpdate` schema: `is_active`
- `ArticleReassign` schema: `author_id`

### Deep Modules to Extract
1. **`app/services/permission_service.py`** — Encapsulates all role-based permission checks. Simple interface: `check_article_permission(user, article, action) -> bool`. Testable in isolation, rarely changes once role matrix is defined.
2. **`app/services/user_management_service.py`** — Handles user invitation, role updates, activation/deactivation. Interface: `invite_user()`, `update_role()`, `toggle_active()`. Testable with mocked email service.

## Testing Decisions

### What Makes a Good Test
- Test external behavior (API responses, permission enforcement), not internal implementation details
- Use SQLite in-memory for backend tests (existing pattern in `tests/conftest.py`)
- Mock email service for invite flow tests
- Test permission matrix exhaustively: each role × each action → expected outcome

### Modules to Test
1. **`permission_service.py`** — Unit tests for all role × action combinations (contributor own article, contributor other's article, editor, admin)
2. **`user_management_service.py`** — Unit tests for invite flow, role updates, activation toggles
3. **Auth router** — Tests for `/api/auth/me` endpoint
4. **Users router** — Tests for all user management endpoints
5. **Articles router** — Integration tests for permission enforcement on article CRUD
6. **Migration** — Test that existing users are correctly migrated to roles
7. **Frontend Pinia store** — Unit tests for user profile storage
8. **Frontend router guards** — Unit tests for role-based route access

### Prior Art
- Backend: `tests/test_auth.py`, `tests/test_articles.py`, `tests/test_rate_limiting.py`
- Frontend: `frontend/src/__tests__/admin.test.ts`, `frontend/src/__tests__/useAdminApi.test.ts`

## Out of Scope

- **OAuth / SSO for multi-author** — OAuth is already implemented for Google/GitHub, but multi-OAuth provider linking is not part of this change
- **Audit logging** — Tracking all admin actions in a separate audit log is a separate feature
- **Article series / collections** — Grouping related articles is out of scope
- **Subscriber segmentation** — Tag-based subscriber targeting is a separate feature
- **A/B testing** — Newsletter subject line testing is out of scope
- **Real-time collaboration** — Multiple users editing the same article simultaneously is out of scope
- **Comment/review system** — Inline comments on drafts for review workflows is out of scope

## Further Notes

- The `require_admin` dependency comment says "In this system, any valid user is an admin for now based on the PRD" — this change fulfills that TODO
- Existing Alembic migrations should be reviewed to ensure the role migration doesn't conflict with prior schema changes
- The frontend's dark tech aesthetic (Space Grotesk, Inter, JetBrains Mono, `#0F0F23` background) should be maintained for the new AdminUsersView
- Invite email template should reuse the existing MJML + Jinja2 email rendering pipeline
- Consider rate limiting the invite endpoint to prevent abuse
