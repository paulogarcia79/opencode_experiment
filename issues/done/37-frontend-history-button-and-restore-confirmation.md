## Parent

PRD: [PRD-article-revision-history.md](../prd/PRD-article-revision-history.md)

## What to build

Integrate the revision panel into the article editor by adding a "History" button and wiring up the slide-out panel. Add a confirmation dialog before restoring a revision to prevent accidental overwrites.

## Acceptance criteria

- [ ] "History" button added to `AdminArticleEditView.vue` (next to Save/Publish buttons)
- [ ] Clicking History opens the `RevisionPanel` slide-out
- [ ] Panel receives the current article's ID and current form state for diff comparison
- [ ] Clicking "Restore this version" in the panel shows a confirmation dialog ("Restore article to version X? This will overwrite your current draft.")
- [ ] Confirming restore calls `useRevisions.restore()`, updates the form with the restored content, and shows a success message
- [ ] After restore, the revision list refreshes to show the new "restore" revision entry
- [ ] Panel closes automatically after successful restore
- [ ] Error handling: shows error message if restore fails
- [ ] Requires design review before merge (HITL)

## Blocked by

- #36 (frontend: revision panel with diff view)
