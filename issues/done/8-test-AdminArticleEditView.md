## Parent

PRD: Frontend Test Coverage (prd/PRD-frontend-test-coverage.md)

## What to build

Tests for the `AdminArticleEditView` component (`frontend/src/views/AdminArticleEditView.vue`). This is the most complex view test. Test new article mode shows "New Article" header, edit mode loads article and populates form, submit in new mode calls `createArticle` and redirects, submit in edit mode calls `updateArticle`, auto-save status indicators render (saving, saved, retrying, error), publish toggle shows/hides newsletter checkbox.

## Acceptance criteria

- [ ] Test file created at `frontend/src/views/__tests__/AdminArticleEditView.spec.ts`
- [ ] Tests new article mode shows "New Article" header
- [ ] Tests edit mode loads article on mount and populates form fields
- [ ] Tests submit in new mode calls `createArticle` and redirects to edit URL
- [ ] Tests submit in edit mode calls `updateArticle`
- [ ] Tests auto-save status indicators render (saving, saved, retrying, error)
- [ ] Tests publish toggle shows/hides newsletter checkbox
- [ ] Mocks: `fetchAdminArticle`, `createArticle`, `updateArticle`, `useAutoSave` (returns `{ status: ref('idle'), retry: vi.fn() }`), `TipTapEditor` (stub), `TagInput` (stub)
- [ ] `beforeEach` clears localStorage and calls `setActivePinia(createPinia())`
- [ ] All tests pass with `cd frontend && npm run test`
- [ ] Existing tests continue to pass

## Blocked by

None - can start immediately
