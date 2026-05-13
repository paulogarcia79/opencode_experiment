## Parent

PRD: `prd/PRD-role-aware-article-ui.md`

## What to build

Make the articles list view role-aware. Contributors see Edit only on their own articles, never see Delete, and see a "View Only" badge on articles they can't edit. Editors and admins see Edit/Delete on all articles as before. Uses the `useArticlePermissions` composable.

## Acceptance criteria

- [ ] `AdminArticlesView.vue` imports `useArticlePermissions` composable
- [ ] Contributors see Edit button only when `canEdit` is true for that article
- [ ] Contributors see "View Only" badge in actions column for articles they can't edit
- [ ] Contributors never see Delete button
- [ ] Editors see Edit and Delete on all articles (unchanged behavior)
- [ ] Admins see Edit and Delete on all articles (unchanged behavior)
- [ ] Frontend test: contributor sees Edit on own article, "View Only" on others
- [ ] Frontend test: contributor never sees Delete button
- [ ] Frontend test: editor/admin sees Edit and Delete on all articles

## Blocked by

- #48-article-permissions-composable
