# Issue 46: Editor Role Permissions + UI

## Parent

Issue #38: Multi-author Support

## What to build

Ensure the editor role has full article management capabilities (create, edit, publish, delete any article, manage tags, import content) but cannot access user management. Verify all existing admin endpoints work correctly with the editor role. Update frontend router guards and UI to allow editors on article/tag/import pages while blocking access to the users management page.

## Acceptance criteria

- [ ] Editors can access `GET /api/admin/articles`, `POST /api/admin/articles`, `PUT /api/articles/{id}`, `DELETE /api/articles/{id}`
- [ ] Editors can publish any article (not just their own)
- [ ] Editors can delete any article (not just their own)
- [ ] Editors can access tag management endpoints (`GET /api/admin/tags`, `DELETE /api/admin/tags/{id}`)
- [ ] Editors can access markdown import endpoint (`POST /api/admin/articles/import`)
- [ ] Editors can access media management endpoints (`GET /api/admin/images`, `POST /api/admin/images`, `DELETE /api/admin/images/{id}`)
- [ ] Editors can access analytics endpoints
- [ ] Editors can access preview email and revision endpoints
- [ ] Editors get 403 on `GET /api/admin/users`, `POST /api/admin/users/invite`, `PUT /api/admin/users/{id}/role`, `PUT /api/admin/users/{id}/active`
- [ ] Editors get 403 on article reassign endpoint (only admins can reassign)
- [ ] Frontend router guards allow editors on articles, media, import, tags, analytics pages
- [ ] Frontend blocks editors from `/admin/users` route (redirects to `/admin`)
- [ ] Admin sidebar hides "Users" link for editors
- [ ] Integration tests verify editor can perform all allowed actions
- [ ] Integration tests verify editor gets 403 on disallowed actions

## Blocked by

- Issue #39: Role Model Migration + Permission Service
- Issue #40: Article Ownership + Author Display
- Issue #41: Auth Me Endpoint + Frontend Role Store
- Issue #42: Contributor Article CRUD (Backend + Frontend)
