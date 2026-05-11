## Parent

PRD: [PRD-article-revision-history.md](../prd/PRD-article-revision-history.md)

## What to build

Build the `RevisionPanel.vue` component — a slide-out panel that shows the revision timeline, allows selecting a revision to preview, and displays a diff view comparing the selected revision against the current article state. Includes a "Restore this version" button.

## Acceptance criteria

- [ ] `RevisionPanel.vue` component in `frontend/src/components/RevisionPanel.vue`
- [ ] Slide-out panel on the right side of the editor (fixed-position overlay or push layout)
- [ ] Timeline list showing version_number, change_type badge (save/publish), title, and formatted timestamp
- [ ] Selecting a revision shows a diff view below the timeline
- [ ] Diff view has three sections: Title, Description, Content
- [ ] Title and description diffs use character-level inline highlighting (red for removed, green for added)
- [ ] Content diff uses word-level plain text comparison (extract text from TipTap JSON via `extract_plain_text_from_tiptap` equivalent)
- [ ] Uses `diff` npm package for diff computation in the browser
- [ ] "Restore this version" button at the bottom of the diff view
- [ ] Panel can be closed (X button or click outside)
- [ ] Loading state while fetching revision data
- [ ] Empty state message when article has no revisions
- [ ] Follows design system: dark tech aesthetic, primary `#7C3AED`, accent `#F43F5E`
- [ ] Requires design review before merge (HITL)

## Blocked by

- #35 (frontend: useRevisions composable)
