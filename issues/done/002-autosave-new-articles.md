---
title: "Auto-Save: Auto-save creation for new articles"
labels:
  - needs-triage
---

## Parent

PRD: `prd/PRD-auto-save-drafts.md`

## What to build

Extend the auto-save system to support brand-new articles that do not yet have a database record.

On the backend, add `POST /api/admin/articles/autosave` to create a new draft article. It should accept the same content fields as the PUT endpoint, generate a unique slug, create the article with `status = "draft"`, handle tags and search_text, and return the generated article ID and slug.

On the frontend, extend `useAutoSave` to handle a `null` article ID: defer the first auto-save until the draft has meaningful content (non-empty title or 60 seconds of active editing with non-empty body content). While deferred, show a subtle UI hint encouraging the user to add a title. Skip saving completely empty drafts. After the first successful creation, trigger a client-side route redirect from `/admin/articles/new` to `/admin/articles/{id}/edit` so subsequent saves target the correct article.

Update the admin edit view to integrate the new-article flow cleanly: initialize the form for a blank new article, handle the redirect without losing editor state, and ensure the status indicator works during the creation phase.

Write tests for the creation endpoint (slug generation, response payload, draft status) and for the composable's first-save flow (deferral logic, empty suppression, redirect callback).

## Acceptance criteria

- [ ] `POST /api/admin/articles/autosave` endpoint exists and requires admin auth.
- [ ] Endpoint generates a unique slug and returns `{ id, slug }` on creation.
- [ ] `useAutoSave` defers first save until title is present or 60s content timeout elapses.
- [ ] Empty new drafts are suppressed — no DB record created for blank forms.
- [ ] After first successful auto-save of a new article, the browser redirects to `/admin/articles/{id}/edit`.
- [ ] Post-redirect, subsequent typing auto-saves to the correct article via PUT.
- [ ] Backend tests cover creation, slug generation, and draft enforcement.
- [ ] Frontend tests cover deferral logic, redirect callback, and empty suppression.

## Blocked by

- `issues/001-core-autosave-existing-drafts.md`
