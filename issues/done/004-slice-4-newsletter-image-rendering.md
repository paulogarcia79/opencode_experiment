# [Slice 4] Newsletter Image Rendering

**GitHub Issue:** #4
**Labels:** needs-triage
**State:** open

## Parent

PRD: Image Upload Feature

## What to build

Ensure images in newsletter emails render correctly with absolute URLs and email-safe inline styles.

## Acceptance criteria

- [ ] tiptap_renderer.py prepends APP_BASE_URL to relative image src attributes
- [ ] Email-safe inline styles added: max-width:100%, height:auto, display:block
- [ ] Newsletter HTML contains absolute URLs for all images
- [ ] Images with external URLs (already absolute) are left unchanged
- [ ] Tests: unit test for renderer with relative URLs, integration test for newsletter generation

## Blocked by

- #1 (Upload API + Storage Backend)
