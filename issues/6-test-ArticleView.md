## Parent

PRD: Frontend Test Coverage (prd/PRD-frontend-test-coverage.md)

## What to build

Tests for the `ArticleView` component (`frontend/src/views/ArticleView.vue`). Test loading state while fetching, error state on fetch failure, success state renders article title/date/reading time, tags render as RouterLinks when present, ShareButtons rendered with correct props, NewsletterForm rendered, useHead called with correct meta data.

## Acceptance criteria

- [ ] Test file created at `frontend/src/views/__tests__/ArticleView.spec.ts`
- [ ] Tests loading state while fetching article
- [ ] Tests error state on fetch failure
- [ ] Tests success state renders article title, date, and reading time
- [ ] Tests tags render as RouterLinks when present
- [ ] Tests ShareButtons rendered with correct props (url, title, description)
- [ ] Tests NewsletterForm component rendered
- [ ] Tests useHead called with correct meta data (title, description, canonical, og, twitter)
- [ ] Mocks: `fetchArticle`, `useHead`, `useReadingTime`, `TipTapRenderer` (stub)
- [ ] All tests pass with `cd frontend && npm run test`
- [ ] Existing tests continue to pass

## Blocked by

None - can start immediately
