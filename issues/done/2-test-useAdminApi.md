## Parent

PRD: Frontend Test Coverage (prd/PRD-frontend-test-coverage.md)

## What to build

Tests for the `useAdminApi` composable (`frontend/src/composables/useAdminApi.ts`). Test all 7 API functions (`fetchAdminArticles`, `fetchAdminArticle`, `createArticle`, `updateArticle`, `deleteArticle`, `fetchAdminImages`, `deleteImage`) with success and error responses. Verify auth header injection using `vi.spyOn(globalThis, 'fetch')`.

## Acceptance criteria

- [ ] Test file created at `frontend/src/composables/__tests__/useAdminApi.spec.ts`
- [ ] Each of the 7 functions tested with successful response
- [ ] Each of the 7 functions tested with error response (non-2xx status)
- [ ] Auth header (`Authorization: Bearer <token>`) verified in fetch calls
- [ ] Uses `vi.spyOn(globalThis, 'fetch')` with mock `Response` objects
- [ ] All tests pass with `cd frontend && npm run test`
- [ ] Existing tests continue to pass

## Blocked by

None - can start immediately
