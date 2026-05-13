## Parent

PRD: `prd/PRD-role-aware-article-ui.md`

## What to build

Make the article edit view role-aware. Contributors are redirected to `/admin` if they try to edit an article they don't own. The "Publish immediately" toggle and "Send newsletter" checkbox are hidden for contributors (always submit `status: 'draft'`). Autosave works correctly for contributors on their own articles. Uses the `useArticlePermissions` composable.

## Acceptance criteria

- [ ] `AdminArticleEditView.vue` imports `useArticlePermissions` composable
- [ ] On mount, if contributor tries to edit an article where `canEdit=false`, redirect to `/admin` with error message
- [ ] "Publish immediately" toggle hidden for contributors (force `status: 'draft'` on submit)
- [ ] "Send newsletter" checkbox hidden for contributors
- [ ] Editors see all controls unchanged
- [ ] Admins see all controls unchanged (including "Change Author" dropdown from #47)
- [ ] Autosave works for contributors creating/editing their own articles
- [ ] Frontend test: contributor redirected when editing non-owned article
- [ ] Frontend test: publish toggle hidden for contributor, visible for editor/admin
- [ ] Frontend test: newsletter checkbox hidden for contributor, visible for editor/admin

## Blocked by

- #48-article-permissions-composable
