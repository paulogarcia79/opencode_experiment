# QA Checklist: Markdown Import

## 1. Prerequisites & Setup

- [ ] Docker dev stack running (`just dev`) — Postgres, Redis, FastAPI, Vite, Nginx
- [ ] Admin user logged in (valid JWT token in localStorage)
- [ ] At least one existing article in the database (for slug collision testing)

---

## 2. Backend API Checks

### POST /api/admin/articles/import

- [ ] **Action:** Send request without auth header → **Expected:** HTTP 401
- [ ] **Action:** POST single `.md` file with YAML frontmatter (title, tags) → **Expected:** HTTP 200, `successes` array with 1 item (id, title, slug), `errors` empty, `total` = 1
- [ ] **Action:** POST multiple `.md` files (mix of valid and invalid) → **Expected:** HTTP 200, valid files in `successes`, invalid files in `errors` with filename + reason, `total` = file count
- [ ] **Action:** POST non-UTF-8 binary file → **Expected:** HTTP 200, file listed in `errors` with "utf-8" message, valid files still imported
- [ ] **Action:** POST file with frontmatter `title` matching existing article slug → **Expected:** Imported article slug auto-renamed with `-2` suffix
- [ ] **Action:** POST file without `title` in frontmatter → **Expected:** Title derived from filename (e.g., `awesome-post.md` → "Awesome Post")
- [ ] **Action:** POST file with `tags: tech, python` in frontmatter → **Expected:** Tags auto-created and attached to article, article created as `draft` status

---

## 3. Frontend UI Checks

### Navigation

- [ ] **Action:** Log in to admin, look at top nav → **Expected:** "Import" link visible between "Articles" and "Media"
- [ ] **Action:** Click "Import" in nav → **Expected:** Navigates to `/admin/import`, page shows "Import Articles" header + drop zone

### Upload Flow

- [ ] **Action:** Drag a `.md` file onto the drop zone → **Expected:** Drop zone highlights (purple border), file imports automatically, loading spinner appears
- [ ] **Action:** Click "Browse files" button, select one `.md` file → **Expected:** File picker opens, file imports, loading spinner appears
- [ ] **Action:** Click "Browse files", select multiple `.md` files → **Expected:** All files imported in single request
- [ ] **Action:** Drag a non-`.md` file (e.g., `.txt`, `.png`) → **Expected:** File ignored, no import triggered

### Results Display

- [ ] **Action:** Import a valid `.md` file → **Expected:** Drop zone hidden, two summary cards shown: "Imported" (green count), "Failed" (red count = 0)
- [ ] **Action:** Import valid file → **Expected:** "Successfully imported" section shows article title as clickable link
- [ ] **Action:** Click an imported article title link → **Expected:** Navigates to `/admin/articles/{id}/edit` with article loaded in editor
- [ ] **Action:** Import mix of valid + invalid files → **Expected:** "Failed imports" section visible with count, click to expand shows each filename + error reason
- [ ] **Action:** Click "Back to Articles" link → **Expected:** Navigates to `/admin` (articles list)

### Error States

- [ ] **Action:** Simulate network failure (stop backend server), then import → **Expected:** Red error banner shows "Import failed" with error message
- [ ] **Action:** After viewing results, drag more files → **Expected:** Drop zone reappears, new import replaces previous results

---

## 4. Edge Cases & Error Handling

- [ ] **Action:** Import file with malformed YAML frontmatter (e.g., `tags: [`) → **Expected:** File listed in errors with parse failure message
- [ ] **Action:** Import file with `![image](https://example.com/photo.png)` remote image → **Expected:** Article imported, image downloaded to `/uploads/{year}/{month}/...`, src rewritten in editor
- [ ] **Action:** Import file with `![image](/uploads/2025/01/existing.png)` local image → **Expected:** Article imported, local URL left unchanged
- [ ] **Action:** Import file with broken remote image URL (404) → **Expected:** Article still imported, original remote URL preserved, error listed in failures
- [ ] **Action:** Import file with SVG image URL → **Expected:** Article imported, SVG URL left unchanged (not downloaded), warning in errors
- [ ] **Action:** Import same `.md` file twice → **Expected:** Two articles created, second one gets `-2` slug suffix
- [ ] **Action:** Import file with `date: 2024-01-15` or `draft: false` in frontmatter → **Expected:** Article still created as `draft` (frontmatter date/draft ignored)
- [ ] **Action:** Import file with GFM table, code block with language, blockquote → **Expected:** Content renders correctly in TipTap editor after import

---

## 5. Integration Checks

- [ ] **Action:** Import a valid `.md` file → **Expected:** Article appears in admin articles list as "draft"
- [ ] **Action:** Import file with tags that don't exist → **Expected:** New tags appear in admin tags page with article count = 1
- [ ] **Action:** Import file, then open in editor → **Expected:** Title, description, tags, and content all pre-populated correctly
- [ ] **Action:** Import file with remote image, then open in editor → **Expected:** Image displays in TipTap editor with local `/uploads/...` URL
- [ ] **Action:** Import file, then publish article → **Expected:** Article publishes normally (newsletter toggle works, no import-related side effects)
