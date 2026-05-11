## Parent

PRD: [PRD-article-revision-history.md](../prd/PRD-article-revision-history.md)

## What to build

Create the `useRevisions` composable that provides the frontend with a clean interface to fetch revision lists, fetch individual revisions, and trigger restores. This composable wraps the API calls and exposes reactive state.

## Acceptance criteria

- [ ] `useRevisions(articleId)` composable in `frontend/src/composables/useRevisions.ts`
- [ ] `fetchList()` method calls `GET /api/admin/articles/{id}/revisions` and returns reactive list
- [ ] `fetch(versionNumber)` method calls `GET /api/admin/articles/{id}/revisions/{version}` and returns full revision data
- [ ] `restore(versionNumber)` method calls `POST /api/admin/articles/{id}/revisions/{version}/restore` and returns the updated article
- [ ] Uses the existing `useAdminApi` composable or equivalent fetch pattern for authenticated requests
- [ ] Handles loading states and errors appropriately
- [ ] Frontend tests in `frontend/src/composables/__tests__/useRevisions.test.ts` covering: fetchList returns revisions, fetch returns full revision, restore calls correct endpoint, error handling
- [ ] Tests use Vitest + `@vue/test-utils` pattern from existing composable tests
- [ ] No `any` types — strict TypeScript interfaces mapping to backend API responses

## Blocked by

- #32 (API: list and get revisions)
- #34 (revision restore service and API)
