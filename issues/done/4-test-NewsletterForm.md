## Parent

PRD: Frontend Test Coverage (prd/PRD-frontend-test-coverage.md)

## What to build

Tests for the `NewsletterForm` component (`frontend/src/components/NewsletterForm.vue`). Test the subscribe flow through all states: initial idle, email input renders, submit calls `subscribeToNewsletter`, loading state during submission, success state with message, error state with message, email cleared after successful subscription.

## Acceptance criteria

- [ ] Test file created at `frontend/src/components/__tests__/NewsletterForm.spec.ts`
- [ ] Tests initial idle state renders correctly
- [ ] Tests email input is present and editable
- [ ] Tests submit calls mocked `subscribeToNewsletter` with email value
- [ ] Tests loading state shown during submission
- [ ] Tests success state with message shown on success
- [ ] Tests error state with message shown on failure
- [ ] Tests email input cleared after successful subscription
- [ ] Uses module-level `vi.mock('@/composables/useApi')`
- [ ] All tests pass with `cd frontend && npm run test`
- [ ] Existing tests continue to pass

## Blocked by

None - can start immediately
