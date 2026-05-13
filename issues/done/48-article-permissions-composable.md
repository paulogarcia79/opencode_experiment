## Parent

PRD: `prd/PRD-role-aware-article-ui.md`

## What to build

Extract a `useArticlePermissions(article)` composable that encapsulates frontend permission logic. It reads the current user's role and id from `useAdminStore`, compares against the article's `author?.id`, and returns `{ canEdit, canDelete, canPublish }`. This deep module mirrors the backend `PERMISSIONS` dict and is the single source of truth for article UI permissions.

## Acceptance criteria

- [ ] `useArticlePermissions(article)` composable created in `frontend/src/composables/useArticlePermissions.ts`
- [ ] Returns `{ canEdit: boolean, canDelete: boolean, canPublish: boolean }` based on user role and article ownership
- [ ] Admin: `canEdit=true`, `canDelete=true`, `canPublish=true` for all articles
- [ ] Editor: `canEdit=true`, `canDelete=true`, `canPublish=true` for all articles
- [ ] Contributor on own article: `canEdit=true`, `canDelete=false`, `canPublish=false`
- [ ] Contributor on others' article: `canEdit=false`, `canDelete=false`, `canPublish=false`
- [ ] Unit tests cover all role × ownership combinations (3 roles × 2 ownership states = 6+ test cases)
- [ ] Tests use Vitest, mock `useAdminStore` to simulate different roles

## Blocked by

None - can start immediately
