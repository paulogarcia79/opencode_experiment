## Parent

PRD: `prd/PRD-post-launch-fixes.md`

## What to build

Make the shared article editor (`AdminArticleEditView`) enter read-only mode when the current user is not the article author. In read-only mode: all text inputs are disabled, the TipTap editor is set to `editable: false`, action buttons (Update Article, Send Preview, Submit for Review) are hidden. The "Change Author" dropdown (admin-only) remains visible. Write Vitest tests.

**End-to-end behavior**: An editor opens a contributor's article from the review queue → editor loads in read-only mode → inputs are disabled, buttons hidden → editor can read the content but cannot modify it. The editor opens their own article → editor is fully editable.

## Acceptance criteria

- [ ] `AdminArticleEditView` has a `isReadOnly` computed: `true` when `article.author?.id !== store.user?.id`
- [ ] In read-only mode: title input is `disabled`
- [ ] In read-only mode: description input is `disabled`
- [ ] In read-only mode: TipTap editor is `editable: false`
- [ ] In read-only mode: TagInput is disabled or hidden
- [ ] In read-only mode: "Update Article" and "Create Article" submit buttons are hidden
- [ ] In read-only mode: "Send Preview" button is hidden
- [ ] In read-only mode: review action buttons (Submit/Update/Re-submit for Review) are hidden
- [ ] Admin "Change Author" dropdown remains visible in read-only mode
- [ ] Non-read-only mode works as before (own article = fully editable)
- [ ] Frontend tests (Vitest): read-only mode disables inputs for non-owner; editor is editable for own article

## Blocked by

- Issue 10 (Article detail endpoint: author eager-load)
