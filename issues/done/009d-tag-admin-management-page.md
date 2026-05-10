# [Slice 3] Tag Admin Management Page

**GitHub Issue:** #009d
**Labels:** needs-triage
**State:** open

## Parent

PRD: Article Tags (`PRD-article-tags.md`)

## What to build

A dedicated admin page for tag hygiene. Add admin endpoints `GET /api/admin/tags` (with article counts) and `DELETE /api/admin/tags/{id}` (returns 409 with count if tag has articles). Build `AdminTagsView` at `/admin/tags` showing a table of all tags (name, slug, article count, created_at). Each row has a delete button. Deleting a used tag triggers a confirmation dialog showing the article count.

## Acceptance criteria

- [ ] `GET /api/admin/tags` returns all tags with article counts
- [ ] `DELETE /api/admin/tags/{id}` on unused tag returns 204
- [ ] `DELETE /api/admin/tags/{id}` on used tag returns 409 with `{detail, article_count}`
- [ ] Admin tags page displays table with name, slug, count, created_at
- [ ] Delete button on unused tag removes it immediately
- [ ] Delete button on used tag shows confirmation dialog with article count
- [ ] After confirming, tag and all associations are removed
- [ ] Backend tests verify list and delete behaviors
- [ ] Frontend tests verify table renders and confirmation dialog works

## Blocked by

- #009a ([Slice 1a] Tag Schema and Basic Article Tagging) — needs tag model
