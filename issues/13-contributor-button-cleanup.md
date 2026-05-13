## Parent

PRD: `prd/PRD-post-launch-fixes.md`

## What to build

Hide the "Update Article" submit button and "Send Preview" button from the article editor when the current user is a contributor. Contributors should only see their review action button (Submit for Review / Update Review / Re-submit for Review) as the submit action. The "Create Article" button for new articles remains visible. Write Vitest tests.

**End-to-end behavior**: A contributor opens their existing article in the editor → sees only the review submit button (e.g., "Submit for Review") → no "Update Article" button → no "Send Preview" button. The contributor creates a new article → sees "Create Article" button (since it's a new article).

## Acceptance criteria

- [ ] Contributor editing an existing article: "Update Article" submit button is hidden
- [ ] Contributor creating a new article: "Create Article" submit button is visible
- [ ] Contributor: "Send Preview" button is always hidden
- [ ] Admin/editor: "Update Article" / "Create Article" and "Send Preview" remain visible as before
- [ ] The review action button (Submit/Update/Re-submit for Review) is the only submit action for contributors on existing articles
- [ ] Frontend tests (Vitest): contributor sees no "Update Article" or "Send Preview"; admin/editor sees both

## Blocked by

None - can start immediately
