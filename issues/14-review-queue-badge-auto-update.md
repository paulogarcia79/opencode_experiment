## Parent

PRD: `prd/PRD-post-launch-fixes.md`

## What to build

Make the review queue badge count in the navigation bar update automatically after an editor/admin approves or rejects an article. Currently the count is fetched once on component mount and never refreshed. After a successful approve/reject, the `ReviewQueue` component re-fetches the count from `GET /api/admin/articles/review/count` and emits a `count-updated` event. The parent `AdminDashboard` and `EditorDashboard` components listen for this event and update their `pendingCount` ref, which updates the badge in the nav.

**End-to-end behavior**: Editor opens review queue → sees badge "3" in nav → approves one article → badge updates to "2" without page refresh → rejects another → badge updates to "1".

## Acceptance criteria

- [ ] `ReviewQueue.vue` emits a `count-updated` event after each successful approve or reject
- [ ] `AdminDashboard.vue` listens for `count-updated` on the ReviewQueue component and re-fetches the count
- [ ] `EditorDashboard.vue` listens for `count-updated` on the ReviewQueue component and re-fetches the count
- [ ] Badge in nav reflects the updated count
- [ ] Re-fetch handles errors silently (badge keeps previous count on failure)
- [ ] Frontend tests (Vitest): approve/reject triggers `count-updated` event emission

## Blocked by

None - can start immediately
