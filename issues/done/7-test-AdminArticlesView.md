## Parent

PRD: Frontend Test Coverage (prd/PRD-frontend-test-coverage.md)

## What to build

Tests for the `AdminArticlesView` component (`frontend/src/views/AdminArticlesView.vue`). Test loading state, empty state with "No articles yet" message, article list renders with title/status/date/edit/delete buttons, delete flow triggers confirmation then calls `deleteArticle`, error state on fetch failure.

## Acceptance criteria

- [ ] Test file created at `frontend/src/views/__tests__/AdminArticlesView.spec.ts`
- [ ] Tests loading state while fetching articles
- [ ] Tests empty state with "No articles yet" message when list is empty
- [ ] Tests article list renders with title, status badge, date, edit and delete buttons
- [ ] Tests delete flow: click delete → confirmation → calls `deleteArticle` → removes from list
- [ ] Tests error state on fetch failure
- [ ] Mocks: `fetchAdminArticles`, `deleteArticle` via module-level `vi.mock('@/composables/useAdminApi')`
- [ ] `beforeEach` clears localStorage and calls `setActivePinia(createPinia())`
- [ ] All tests pass with `cd frontend && npm run test`
- [ ] Existing tests continue to pass

## Blocked by

None - can start immediately
