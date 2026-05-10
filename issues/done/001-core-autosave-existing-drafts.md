---
title: "Auto-Save: Core auto-save for existing drafts"
labels:
  - needs-triage
---

## Parent

PRD: `prd/PRD-auto-save-drafts.md`

## What to build

Build the foundational end-to-end auto-save flow for existing draft articles.

On the backend, create a dedicated auto-save service that enforces `status = "draft"` and bypasses newsletter logic. Expose it via `PUT /api/admin/articles/{id}/autosave`. The endpoint should accept title, description, content (TipTap JSON), and tag_names; unconditionally set status to draft; generate/reuse the article slug; handle tag associations; rebuild search_text; and return a lightweight success payload.

On the frontend, create the `useAutoSave` composable that wraps the auto-save lifecycle for an existing article: detect form changes, debounce for 2 seconds after the user stops typing, skip saves when the form is empty or unchanged since the last successful save, call the PUT auto-save endpoint, and expose a reactive status state. Also add thin wrapper functions for the auto-save endpoints to the existing admin API client.

Integrate `useAutoSave` into the admin article edit view. Render a subtle status indicator near the action buttons that shows "Saving..." during active saves and "Saved" briefly after success. Ensure the existing manual "Update Article" button continues to work for explicit publishes.

Write tests for the backend endpoint (auth, draft enforcement, tag handling, response shape) and for the composable (dirty detection, debounce timing with fake timers, empty-form suppression, status transitions).

## Acceptance criteria

- [ ] `PUT /api/admin/articles/{id}/autosave` endpoint exists and requires admin auth.
- [ ] Endpoint unconditionally forces `status = "draft"` even if a published status is passed.
- [ ] Endpoint bypasses newsletter sending logic entirely.
- [ ] `useAutoSave` composable exists with debounced save (2s) and dirty/empty detection.
- [ ] Admin edit view shows "Saving..." / "Saved" status indicator.
- [ ] Existing manual save/publish flow remains untouched and functional.
- [ ] Backend tests cover endpoint behavior and draft enforcement.
- [ ] Frontend tests cover composable debounce, dirty detection, and status states.

## Blocked by

None — can start immediately.
