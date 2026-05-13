# Issue 44: Admin Users Management UI

## Parent

Issue #38: Multi-author Support

## What to build

Create the `AdminUsersView.vue` page for managing team members: a table listing all users with their email, role, status, and creation date. Include an "Invite User" modal with email input and role selector, inline role dropdown for changing roles, and a toggle for deactivating/reactivating users. This page is accessible only to admins.

## Acceptance criteria

- [ ] `AdminUsersView.vue` displays a table of all users with columns: email, role, status (verified/pending), active/inactive, created date
- [ ] "Invite User" button opens a modal with email input and role dropdown (admin/editor/contributor)
- [ ] Invite form validates email format, shows loading state, displays success/error messages
- [ ] Role dropdown inline-editable per user (saves on change, shows loading state)
- [ ] Active/inactive toggle per user (deactivates immediately, shows confirmation for deactivate)
- [ ] Deactivated users shown with visual indicator (greyed out, "Inactive" badge)
- [ ] Route `/admin/users` added to router with admin-only guard (redirects non-admins)
- [ ] Admin sidebar navigation includes "Users" link (visible only to admins)
- [ ] Uses existing dark tech aesthetic (Space Grotesk headings, Inter body, `#0F0F23` background, `#7C3AED` primary)
- [ ] API functions added to `useAdminApi.ts` for user management
- [ ] Tests for AdminUsersView component (render, invite flow, role change, deactivate)
- [ ] Tests for admin-only route guard

## Blocked by

- Issue #43: User Management API + Invite Flow
