## Parent

PRD: Markdown Import (prd/PRD-markdown-import.md)

## What to build

Dedicated `/admin/import` page with drag-and-drop file upload for Markdown files. Single endpoint call to `POST /api/admin/articles/import`, then display results showing success count, error count, collapsible error list with reasons, and links to each imported article in the editor. Add nav link in AdminLayout.

## Acceptance criteria

- [ ] `AdminImportView.vue` created at `/admin/import` route
- [ ] Drag-and-drop upload area accepting `.md` files (single + multiple)
- [ ] File input fallback button for browse-to-upload
- [ ] Loading/progress indicator while files are being processed
- [ ] Results section displays: success count, error count
- [ ] Collapsible error list showing filename + error reason for each failure
- [ ] Each successfully imported article shown with a link to its editor page (`/admin/articles/{id}/edit`)
- [ ] "Back to Articles" link to return to `/admin`
- [ ] `useMarkdownImport.ts` composable wrapping the API call
- [ ] "Import" nav link added to `AdminLayout.vue` between "Articles" and "Media"
- [ ] Page matches dark tech aesthetic (background `#0F0F23`, primary `#7C3AED`)
- [ ] Router entry added under admin layout with `requiresAuth: true`

## Blocked by

- #1 - Backend Import Service + Endpoint
