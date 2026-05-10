# [Slice 3] Media Library Admin Page

**GitHub Issue:** #3
**Labels:** needs-triage
**State:** open

## Parent

PRD: Image Upload Feature

## What to build

An admin page at /admin/media for browsing, uploading, copying URLs, and deleting image assets.

## Acceptance criteria

- [ ] GET /api/admin/images endpoint with pagination
- [ ] DELETE /api/admin/images/{id} endpoint removes file from storage + DB record
- [ ] Admin /admin/media page with responsive image grid
- [ ] Upload button opening file picker
- [ ] Copy URL button for each image
- [ ] Delete button with confirmation dialog
- [ ] Tests: integration tests for list and delete endpoints, Vitest component tests for grid

## Blocked by

- #1 (Upload API + Storage Backend)
