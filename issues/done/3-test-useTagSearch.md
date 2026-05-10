## Parent

PRD: Frontend Test Coverage (prd/PRD-frontend-test-coverage.md)

## What to build

Tests for the `useTagSearch` composable (`frontend/src/composables/useTagSearch.ts`). Test `fetchSuggestions` with empty query returns empty, with query returns suggestions, loading state toggles correctly, and error state handled gracefully.

## Acceptance criteria

- [ ] Test file created at `frontend/src/composables/__tests__/useTagSearch.spec.ts`
- [ ] Tests empty query returns empty suggestions
- [ ] Tests non-empty query fetches and returns suggestions
- [ ] Tests loading state toggles (false → true → false)
- [ ] Tests error state handled gracefully (suggestions stay empty on failure)
- [ ] Uses `vi.spyOn(globalThis, 'fetch')` with mock `Response` objects
- [ ] All tests pass with `cd frontend && npm run test`
- [ ] Existing tests continue to pass

## Blocked by

None - can start immediately
