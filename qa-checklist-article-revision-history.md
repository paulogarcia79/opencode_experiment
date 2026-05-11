# QA Checklist: Article Revision History

## 1. Prerequisites & Setup

- [ ] Backend dev server running (`just back` or `just dev`)
- [ ] Frontend dev server running (`just front` or `just dev`)
- [ ] Admin user logged in with valid session/token
- [ ] At least one draft article exists in the system

---

## 2. Backend API Checks

### List Revisions
- [ ] **Action:** `GET /api/admin/articles/{id}/revisions` with valid admin token → **Expected:** 200, array of `{version_number, change_type, title, created_at}`, no `content` field
- [ ] **Action:** `GET /api/admin/articles/{id}/revisions` without auth → **Expected:** 401
- [ ] **Action:** `GET /api/admin/articles/{nonexistent-id}/revisions` → **Expected:** 404

### Get Single Revision
- [ ] **Action:** `GET /api/admin/articles/{id}/revisions/{version}` with valid admin token → **Expected:** 200, full revision with `{version_number, change_type, title, content, description, tag_names, created_at}`
- [ ] **Action:** `GET /api/admin/articles/{id}/revisions/999` → **Expected:** 404
- [ ] **Action:** `GET /api/admin/articles/{id}/revisions/{version}` without auth → **Expected:** 401

### Restore Revision
- [ ] **Action:** `POST /api/admin/articles/{id}/revisions/{version}/restore` → **Expected:** 200, updated article object with restored title/content/tags
- [ ] **Action:** `POST /api/admin/articles/{id}/revisions/999/restore` → **Expected:** 404
- [ ] **Action:** `POST /api/admin/articles/{id}/revisions/{version}/restore` without auth → **Expected:** 401

### Revision Creation on Save/Publish
- [ ] **Action:** `PUT /api/articles/{id}` with `{"title": "Updated"}` (draft save) → **Expected:** A new revision with `change_type: "save"` is created
- [ ] **Action:** `PUT /api/articles/{id}` with `{"status": "published"}` (publish) → **Expected:** A new revision with `change_type: "publish"` is created
- [ ] **Action:** `PUT /api/admin/articles/{id}/autosave` with updated data → **Expected:** No new revision created (revisions list unchanged)

---

## 3. Frontend UI Checks

### History Button
- [ ] **Action:** Navigate to `/admin/articles/{id}/edit` for an existing article → **Expected:** "History" button visible in the actions bar (next to Save/Preview buttons)
- [ ] **Action:** Navigate to `/admin/articles/new/edit` → **Expected:** No "History" button shown (new article, no revisions yet)

### Revision Panel
- [ ] **Action:** Click "History" button → **Expected:** Slide-out panel opens from the right side with dark overlay
- [ ] **Action:** Panel shows revision list → **Expected:** Each entry displays version number (v1, v2...), change type badge (save/publish/restore), title, and formatted timestamp
- [ ] **Action:** Click a revision in the list → **Expected:** Selected revision highlighted, diff view appears below
- [ ] **Action:** Panel shows diff for title → **Expected:** Character-level diff with green (added) and red strikethrough (removed) highlighting
- [ ] **Action:** Panel shows diff for description → **Expected:** Character-level diff with green/red highlighting
- [ ] **Action:** Panel shows diff for content → **Expected:** Word-level plain text diff with green/red highlighting
- [ ] **Action:** Panel shows diff for tags → **Expected:** Tag badges — green for added, red/strikethrough for removed, gray for unchanged
- [ ] **Action:** Click outside panel overlay → **Expected:** Panel closes
- [ ] **Action:** Click X button in panel header → **Expected:** Panel closes

### Restore Flow
- [ ] **Action:** Click "Restore this version" button → **Expected:** Confirmation dialog appears with message "Restore article to version X? This will overwrite your current draft."
- [ ] **Action:** Click "Cancel" in confirmation → **Expected:** Dialog closes, article unchanged
- [ ] **Action:** Click "Restore" in confirmation → **Expected:** Article form fields (title, description, content, tags) update to restored values, success message "Article restored to previous version" shown, panel closes
- [ ] **Action:** Reopen History panel after restore → **Expected:** New revision with "restore" badge appears at top of list

### Empty/Error States
- [ ] **Action:** Open History panel for article with no revisions → **Expected:** "No revisions yet" message shown
- [ ] **Action:** Open panel with network disconnected → **Expected:** Error message displayed

---

## 4. Edge Cases & Error Handling

- [ ] **Action:** Save article multiple times rapidly → **Expected:** Each save creates a separate revision with sequential version numbers
- [ ] **Action:** Publish a draft, then save again → **Expected:** Publish revision and subsequent save revision both present, correctly typed
- [ ] **Action:** Restore to v1, then restore to v2 → **Expected:** Both restores create new "restore" revision entries, article state matches each target
- [ ] **Action:** Restore an article that was published → **Expected:** Article status remains "published", `published_at` unchanged, only content/tags revert
- [ ] **Action:** Restore article with tags that don't exist → **Expected:** Tags are recreated via `get_or_create_tags`, no error
- [ ] **Action:** Access revision endpoints with expired/invalid token → **Expected:** 401 Unauthorized
- [ ] **Action:** Restore with invalid version number (negative, zero) → **Expected:** 404

---

## 5. Integration Checks

- [ ] **Action:** Create article → Edit title → Save → Edit description → Save → Publish → **Expected:** 3 revisions exist: save (title change), save (description change), publish
- [ ] **Action:** Restore to first revision → **Expected:** Title, description, and content all revert to original values simultaneously
- [ ] **Action:** Restore to revision with different tags → **Expected:** Tags update to match the restored revision, search index reflects new tags
- [ ] **Action:** After restore, save the article again → **Expected:** New "save" revision created capturing the post-restore state
- [ ] **Action:** Delete an article → **Expected:** All associated revisions are deleted (CASCADE)
- [ ] **Action:** Full flow: create article → make 3 edits → restore to v1 → verify form content matches v1 → save again → verify 5th revision exists → **Expected:** All steps succeed without errors
