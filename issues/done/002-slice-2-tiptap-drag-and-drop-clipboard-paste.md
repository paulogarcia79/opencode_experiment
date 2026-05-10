# [Slice 2] TipTap Drag-and-Drop + Clipboard Paste

**GitHub Issue:** #2
**Labels:** needs-triage
**State:** open

## Parent

PRD: Image Upload Feature

## What to build

Enable image insertion in the TipTap editor via drag-and-drop and clipboard paste. Images upload asynchronously and replace loading placeholders on success.

## Acceptance criteria

- [ ] handleDrop handler in TipTap editor extracts File objects from drag events
- [ ] handlePaste handler detects image paste from clipboard
- [ ] Both handlers POST to /api/admin/images endpoint
- [ ] Loading placeholder node shown during upload, replaced with real image on success
- [ ] Max-width CSS constraint (100% container width) applied to editor images
- [ ] Click-to-select image node + Delete key removes it
- [ ] Tests: Vitest unit tests for handlers, E2E test for drag-and-drop flow

## Blocked by

- #1 (Upload API + Storage Backend)
