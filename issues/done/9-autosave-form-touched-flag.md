## Parent

PRD: `prd/PRD-post-launch-fixes.md`

## What to build

Add a `formTouched` flag to the `useAutoSave` composable so auto-save only triggers when the user has actually made edits. Currently, loading an existing article in the editor mutates `form.value` during `onMounted`, which fires the auto-save watch after 2 seconds — silently reverting published and pending_review articles to draft. The `formTouched` flag defaults to `false` and the watch only calls `doSave()` when `formTouched === true`. The composable exposes a `markFormTouched()` function that the editor calls when the user interacts (input, content change). Write Vitest tests.

**End-to-end behavior**: An editor opens a published article in the editor. No auto-save fires. The editor clicks into the title field and types — `formTouched` becomes `true` — 2 seconds later auto-save fires normally.

## Acceptance criteria

- [ ] `useAutoSave` composable has a `formTouched` ref (default `false`)
- [ ] The `watch` callback that triggers `doSave()` checks `formTouched === true` before proceeding
- [ ] The composable exposes `markFormTouched()` in its return value
- [ ] `AdminArticleEditView` calls `markFormTouched()` on user interaction events (title input, description input, TipTap `onUpdate`)
- [ ] `onMounted` populating the form from a loaded article does NOT call `markFormTouched()`
- [ ] Auto-save still works normally for new articles after user types
- [ ] Frontend tests (Vitest): auto-save does NOT fire when `formTouched` is false; auto-save fires when `formTouched` is true and form changes

## Blocked by

None - can start immediately
