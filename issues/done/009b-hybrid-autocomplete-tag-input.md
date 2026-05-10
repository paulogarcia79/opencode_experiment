# [Slice 1b] Hybrid Autocomplete Tag Input

**GitHub Issue:** #009b
**Labels:** needs-triage
**State:** open

## Parent

PRD: Article Tags (`PRD-article-tags.md`)

## What to build

Replace the simple comma-separated tag input with a proper multi-select chip input with hybrid autocomplete. As the admin types, existing tags are suggested from `GET /api/admin/tags` (150ms debounce). Pressing Enter or clicking a suggestion selects/creates a tag. Tags render as removable chips inside the input. The input hard-caps at 8 tags and disables once the limit is reached.

## Acceptance criteria

- [ ] Typing in the tag input shows a dropdown with matching existing tags
- [ ] Pressing Enter creates a new tag if no suggestion matches
- [ ] Clicking a suggestion selects the existing tag
- [ ] Max 8 tags — input disables once limit reached
- [ ] Backspace removes the last chip
- [ ] Clicking the × on a chip removes it
- [ ] Selected tags are submitted with the article create/update payload
- [ ] Frontend tests verify suggestions render, chip creation, max limit, and chip removal

## Blocked by

- #009a ([Slice 1a] Tag Schema and Basic Article Tagging) — needs tag model and API endpoints
