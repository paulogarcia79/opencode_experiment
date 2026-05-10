## Parent

PRD: Frontend Test Coverage (prd/PRD-frontend-test-coverage.md)

## What to build

Tests for the admin Pinia store (`frontend/src/stores/admin.ts`). Verify token initialization from localStorage, `setToken` persists to localStorage, and `clearToken` removes from localStorage and resets value.

## Acceptance criteria

- [ ] Test file created at `frontend/src/stores/__tests__/admin.spec.ts`
- [ ] Tests token initialization from localStorage on store creation
- [ ] Tests `setToken` updates value and persists to localStorage
- [ ] Tests `clearToken` resets value to empty string and removes from localStorage
- [ ] `beforeEach` clears localStorage and calls `setActivePinia(createPinia())`
- [ ] All tests pass with `cd frontend && npm run test`
- [ ] Existing tests continue to pass

## Blocked by

None - can start immediately
