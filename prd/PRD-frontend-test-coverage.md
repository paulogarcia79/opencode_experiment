## Problem Statement

Frontend test coverage is incomplete. While 12 test files exist covering composables (useAutoSave, useImageUpload, useHead, useReadingTime, useSearch) and some views/components (ShareButtons, TagInput, AdminMediaView, AdminTagsView, HomeView, SearchView, TagArticlesView), critical units remain untested. The public-facing `ArticleView.vue` (article detail page), the admin article management views (`AdminArticleEditView.vue`, `AdminArticlesView.vue`), key components (`NewsletterForm.vue`, `TipTapRenderer.vue`), the Pinia admin store, and API composables (`useAdminApi.ts`, `useTagSearch.ts`) have zero test coverage. This means regressions in article rendering, admin CRUD flows, newsletter subscription, and authentication state can slip through undetected.

## Solution

Add 8 new test files covering the untested frontend units, following the existing testing patterns (Vitest + @vue/test-utils, happy-dom environment, module-level mocking). Tests will be shallow — verifying behaviors and integration points rather than CSS classes or exact DOM structure. TipTapEditor testing is deferred to a separate change due to its complexity with @tiptap/vue-3 mocking.

## User Stories

1. As a developer, I want tests for the admin Pinia store, so that I can verify token persistence and clearing works correctly across sessions
2. As a developer, I want tests for `useAdminApi`, so that I can verify admin API calls include proper auth headers and handle errors correctly
3. As a developer, I want tests for `useTagSearch`, so that I can verify tag suggestion fetching works with debounced queries
4. As a developer, I want tests for `NewsletterForm`, so that I can verify the subscribe flow handles success, loading, and error states
5. As a developer, I want tests for `TipTapRenderer`, so that I can verify TipTap JSON renders to HTML correctly
6. As a developer, I want tests for `ArticleView`, so that I can verify the article detail page shows loading, error, and success states with correct data
7. As a developer, I want tests for `AdminArticleEditView`, so that I can verify the create and edit article flows work correctly including auto-save status indicators
8. As a developer, I want tests for `AdminArticlesView`, so that I can verify the admin article listing shows loading, empty, list, and error states, and that delete flow works
9. As a developer, I want tests that mock composables at the module level, so that each test file is fast and isolated
10. As a developer, I want tests that use `vi.spyOn(globalThis, 'fetch')` for composable tests, so that I can verify actual fetch calls, headers, and response handling
11. As a developer, I want tests that clear localStorage and reset Pinia between runs, so that tests are isolated and reproducible
12. As a developer, I want one test file per unit, so that tests are discoverable and easy to maintain

## Implementation Decisions

### Test Files to Create

**Store Tests:**
- `frontend/src/stores/__tests__/admin.spec.ts` — Tests for `useAdminStore`: token initialization from localStorage, `setToken` persists to localStorage, `clearToken` removes from localStorage and resets value

**Composable Tests:**
- `frontend/src/composables/__tests__/useAdminApi.spec.ts` — Tests for each admin API function: `fetchAdminArticles`, `fetchAdminArticle`, `createArticle`, `updateArticle`, `deleteArticle`, `fetchAdminImages`, `deleteImage`. Each function tested with successful response and error response. Auth header injection verified via `vi.spyOn(globalThis, 'fetch')`.
- `frontend/src/composables/__tests__/useTagSearch.spec.ts` — Tests for `useTagSearch`: `fetchSuggestions` with empty query returns empty, with query returns suggestions, loading state toggles correctly, error state handled gracefully

**Component Tests:**
- `frontend/src/components/__tests__/NewsletterForm.spec.ts` — Tests: initial idle state, email input renders, submit calls `subscribeToNewsletter`, shows loading state during submission, shows success state with message on success, shows error state with message on failure, clears email after successful subscription
- `frontend/src/components/__tests__/TipTapRenderer.spec.ts` — Tests: renders TipTap JSON to HTML, renders empty content gracefully, handles null/undefined content

**View Tests:**
- `frontend/src/views/__tests__/ArticleView.spec.ts` — Tests: loading state while fetching, error state on fetch failure, success state renders article title/date/reading time, tags render as RouterLinks when present, ShareButtons component rendered with correct props, NewsletterForm component rendered, useHead called with correct meta data. Mocks: `fetchArticle`, `useHead`, `useReadingTime`, `TipTapRenderer` (stub).
- `frontend/src/views/__tests__/AdminArticleEditView.spec.ts` — Tests: new article mode shows "New Article" header, edit mode loads article and populates form, submit in new mode calls `createArticle` and redirects, submit in edit mode calls `updateArticle`, auto-save status indicators render (saving, saved, retrying, error), publish toggle shows/hides newsletter checkbox. Mocks: `fetchAdminArticle`, `createArticle`, `updateArticle`, `useAutoSave`, `useAdminApi`, `TipTapEditor` (stub), `TagInput` (stub).
- `frontend/src/views/__tests__/AdminArticlesView.spec.ts` — Tests: loading state, empty state with "No articles yet" message, article list renders with title/status/date/edit/delete buttons, delete flow triggers confirmation then calls `deleteArticle`, error state on fetch failure. Mocks: `fetchAdminArticles`, `deleteArticle`, `useAdminApi`.

### Mocking Strategy

- **Composable tests themselves** use `vi.spyOn(globalThis, 'fetch')` with mock `Response` objects to verify actual fetch behavior, headers, and response parsing.
- **Component and view tests** use module-level `vi.mock()` to mock composables (e.g., `vi.mock('@/composables/useApi')`, `vi.mock('@/composables/useAdminApi')`). This isolates the component under test and matches existing patterns.
- **TipTapRenderer** is mocked as a stub in parent view tests (ArticleView, AdminArticleEditView) using `vi.mock('@/components/TipTapRenderer.vue')`.
- **TipTapEditor** and **TagInput** are mocked as stubs in AdminArticleEditView tests.
- **useAutoSave** is mocked to return `{ status: ref('idle'), retry: vi.fn() }` in AdminArticleEditView tests.

### Test Setup

- `beforeEach` clears `localStorage` and calls `setActivePinia(createPinia())` for test isolation.
- All tests use `happy-dom` environment (configured in `vite.config.ts`).
- Async operations use `flushPromises()` from `@vue/test-utils`.

### Test Depth

Tests are **shallow** — they verify behaviors and integration points, not CSS classes, exact DOM structure, or styling. For example:
- Assert that a loading message appears, not that a specific SVG spinner is rendered
- Assert that an article title is displayed, not that it has `text-3xl font-display` classes
- Assert that a button click triggers an API call, not that the button has a specific hover state

## Testing Decisions

**What makes a good test:** Test external behavior through public interfaces. For composables, verify that fetch is called with correct URLs, methods, and headers, and that the returned data is correctly parsed. For components, verify that props are passed correctly, events are emitted, and state transitions render the expected UI. Do not test internal implementation details, CSS classes, or exact DOM structure.

**Modules to test:**
- `admin.ts` store: token initialization, setToken, clearToken, localStorage persistence
- `useAdminApi`: all 7 API functions with success and error responses, auth header injection
- `useTagSearch`: fetchSuggestions with various query states, loading/error state management
- `NewsletterForm`: subscribe flow through all states (idle → loading → success/error)
- `TipTapRenderer`: TipTap JSON to HTML rendering, edge cases (empty, null)
- `ArticleView`: loading/error/success states, tags, meta tags, child component rendering
- `AdminArticleEditView`: create/edit modes, form submission, auto-save status, publish toggle
- `AdminArticlesView`: loading/empty/list/error states, delete confirmation flow

**Prior art:**
- Backend tests use `TestClient` + `session` fixtures (see `test_articles.py`, `test_images.py`)
- Frontend tests use `@vue/test-utils` with `flushPromises` for async behavior (see `AdminMediaView.spec.ts`, `ShareButtons.spec.ts`, `HomeView.spec.ts`)
- Composable mocking pattern established in existing tests (see `HomeView.spec.ts` mocking `useApi`)

## Out of Scope

- **TipTapEditor testing** — Deferred due to complexity of mocking @tiptap/vue-3 editor instance. Will be its own change.
- **E2E tests** — Playwright tests for critical user flows are a separate infrastructure change.
- **Test coverage reporting** — No coverage threshold enforcement or CI integration yet.
- **AdminLoginView, ConfirmView, UnsubscribeView testing** — These views are lower priority and will be covered in a future change.
- **useApi composable testing** — The public API composable (non-admin) is lower priority since it's simpler and well-exercised through view tests.
- **CSS/styling assertions** — Tests verify behavior, not visual appearance.

## Further Notes

- The `admin.ts` store is the simplest unit to test and should be implemented first to establish patterns.
- `useAdminApi` and `useTagSearch` composables call `fetch` directly — spying on `globalThis.fetch` is the most direct testing approach.
- `NewsletterForm` is the simplest component to test and serves as a good bridge between composable and view tests.
- `AdminArticleEditView` is the most complex view test — it has the most mocks and the most test scenarios. Consider implementing it last after patterns are established.
- All existing 12 test files should continue to pass — no existing test files are modified.
- Run `cd frontend && npm run test` to verify all tests pass after implementation.
