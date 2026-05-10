# Manual QA Checklist: Auto-Save Drafts

## 1. Prerequisites & Setup

- [ ] **Backend running:** FastAPI dev server on `:8000` (or via Docker Compose with `just dev`)
- [ ] **Frontend running:** Vite dev server on `:5173` (or via Docker Compose)
- [ ] **Database:** PostgreSQL running with latest migrations applied
- [ ] **Admin auth:** Valid `ADMIN_API_TOKEN` set in `.env` and copied to clipboard for API testing
- [ ] **Browser:** Modern browser with DevTools Network tab open
- [ ] **Initial state:** At least one existing draft article in the database for testing PUT endpoint

---

## 2. Backend API Checks

### 2.1 POST /api/admin/articles/autosave — Create new draft

- [ ] **Action:** Send `POST /api/admin/articles/autosave` with valid Bearer token and payload:
  ```json
  {
    "title": "QA Test Article",
    "content": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]}]},
    "description": "QA test",
    "tag_names": ["test"]
  }
  ```
  → **Expected:** HTTP 200, response contains `id` (UUID), `slug` ("qa-test-article"), `status`: "draft", and `tags` array with test tag

- [ ] **Action:** Send same POST without Bearer token → **Expected:** HTTP 401
- [ ] **Action:** Send same POST with invalid Bearer token → **Expected:** HTTP 403
- [ ] **Action:** Check database `articles` table for newly created row → **Expected:** `status` = "draft", `published_at` = NULL, `send_newsletter` = false

### 2.2 PUT /api/admin/articles/{id}/autosave — Update existing draft

- [ ] **Action:** Send `PUT /api/admin/articles/{existing-id}/autosave` with valid token and updated title/description/tags → **Expected:** HTTP 200, response reflects updated fields, `status` remains "draft"

- [ ] **Action:** Send PUT to non-existent UUID → **Expected:** HTTP 404
- [ ] **Action:** Send PUT without auth → **Expected:** HTTP 401

### 2.3 Draft enforcement (critical safety check)

- [ ] **Action:** Create a published article via normal endpoint, then send `PUT /api/admin/articles/{published-id}/autosave` with any update → **Expected:** HTTP 200, but response shows `status` = "draft" and `published_at` = null (article is UNPUBLISHED by auto-save)

- [ ] **Action:** Verify no newsletter email was triggered after auto-save update → **Expected:** No email in Resend logs / mailpit

---

## 3. Frontend UI Checks

### 3.1 New article auto-save flow

- [ ] **Action:** Navigate to `/admin/articles/new` → **Expected:** Page shows "New Article" heading, form is blank, no article ID in URL
- [ ] **Action:** Type a title in the title field, wait 2 seconds without clicking anything → **Expected:** Status indicator shows "Saving..." briefly, then "Saved"; URL silently changes to `/admin/articles/{id}/edit`
- [ ] **Action:** After redirect, type more content in the editor, wait 2 seconds → **Expected:** "Saving..." → "Saved" cycle repeats; no page reload
- [ ] **Action:** Refresh the page after auto-save redirect → **Expected:** Form reloads with previously auto-saved content intact

### 3.2 Existing article auto-save flow

- [ ] **Action:** Open an existing draft article via `/admin/articles/{id}/edit` → **Expected:** "Edit Article" heading, form populated with article data
- [ ] **Action:** Change the title, wait 2 seconds → **Expected:** "Saving..." → "Saved" appears near action buttons
- [ ] **Action:** Check that manual "Update Article" button still works → **Expected:** Clicking it publishes the article (if publish toggle is on) and shows success message

### 3.3 Status indicator states

- [ ] **Action:** Type continuously for 5 seconds, stop typing → **Expected:** After ~2s of idle, "Saving..." appears; after success, "Saved" appears in emerald green
- [ ] **Action:** Block the `/api/admin/articles/{id}/autosave` endpoint in DevTools (e.g., block URL) and type → **Expected:** After initial failure, "Auto-save failed (retrying...)" appears in amber
- [ ] **Action:** Keep the endpoint blocked for 10+ seconds → **Expected:** After 3 retries, status changes to "Auto-save failed" in red with a "Retry" button
- [ ] **Action:** Click the "Retry" button → **Expected:** Immediate re-attempt, status returns to "Saving..."
- [ ] **Action:** Unblock the endpoint and type again → **Expected:** Auto-save resumes normally

### 3.4 New article deferral hint

- [ ] **Action:** Navigate to `/admin/articles/new`, leave title empty, type content in editor → **Expected:** Status area shows "Add a title to enable auto-save" in gray
- [ ] **Action:** Wait 60+ seconds without adding a title → **Expected:** Auto-save eventually triggers (creates draft with "Untitled" slug), URL redirects

---

## 4. Edge Cases & Error Handling

### 4.1 Empty form suppression

- [ ] **Action:** Navigate to `/admin/articles/new`, leave everything blank, wait 10 seconds → **Expected:** No auto-save triggered, no new article in database, URL unchanged
- [ ] **Action:** Type a title, then delete it back to empty, wait → **Expected:** No save triggered for empty form

### 4.2 Unchanged form suppression

- [ ] **Action:** Open existing draft, make one change, wait for "Saved" → **Expected:** One API call made
- [ ] **Action:** Wait another 10 seconds without typing → **Expected:** No additional API calls (form unchanged since last save)
- [ ] **Action:** Type the exact same title again → **Expected:** Still no API call (payload is byte-equal)

### 4.3 Network failure scenarios

- [ ] **Action:** Turn off backend server mid-editing → **Expected:** "Auto-save failed (retrying...)" appears, user can keep typing
- [ ] **Action:** Turn server back on during retry phase → **Expected:** Next retry succeeds, status returns to "Saved"
- [ ] **Action:** Turn server off, exhaust all 3 retries, then turn back on and click "Retry" → **Expected:** Manual retry succeeds immediately

### 4.4 Auth expiration

- [ ] **Action:** Clear localStorage admin token while editing → **Expected:** Next auto-save attempt fails with 401, status shows error
- [ ] **Action:** Re-login and return to editor → **Expected:** Typing resumes auto-save with new token

---

## 5. Integration Checks

### 5.1 End-to-end new article flow

- [ ] **Action:** Create new article → type title → wait for auto-save redirect → add tags → add content → wait for auto-save → navigate away → return via admin list → open article → **Expected:** All content (title, tags, body) persisted correctly

### 5.2 Publish toggle isolation

- [ ] **Action:** Edit an existing draft, toggle "Publish immediately" ON, type some content, wait for auto-save → **Expected:** Article remains draft (auto-save does NOT publish); "Publish immediately" toggle state is preserved
- [ ] **Action:** Click "Update Article" with publish toggle ON → **Expected:** Article is actually published, newsletter may be sent (normal publish flow)

### 5.3 Database state verification

- [ ] **Action:** Auto-save an article, then query database:
  ```sql
  SELECT status, published_at, updated_at FROM articles WHERE slug = 'your-test-slug';
  ```
  → **Expected:** `status` = 'draft', `published_at` IS NULL, `updated_at` is recent

### 5.4 Public site isolation

- [ ] **Action:** Auto-save a draft with distinctive title → check public site (`/api/articles`, `/feed.xml`, `/sitemap.xml`) → **Expected:** Draft does NOT appear in any public endpoint
- [ ] **Action:** Publish the same article manually → check public endpoints again → **Expected:** Article now appears

### 5.5 Tag handling

- [ ] **Action:** Auto-save with 5 tags → check database tag associations → **Expected:** All 5 tags linked to article
- [ ] **Action:** Auto-save with 9 tags → **Expected:** Backend rejects with validation error (max 8), frontend shows error

### 5.6 Heartbeat verification

- [ ] **Action:** Open DevTools Network tab, type one character then keep typing every second for 35 seconds → **Expected:** One debounced save at ~2s, plus one heartbeat save at ~30s (total 2 PUT requests, not dozens)

---

## Sign-off

| Tester | Date | Result |
|--------|------|--------|
|        |      | PASS / FAIL |

**Notes:**
