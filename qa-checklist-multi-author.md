# QA Checklist: Multi-Author Support

## 1. Prerequisites & Setup

- [ ] **Verify:** Docker dev stack is running (`just dev`) — PostgreSQL, Redis, Backend, Frontend, Nginx
- [ ] **Verify:** Database migrations applied (`just migrate`) — new columns `role`, `is_active`, `author_id`, `setup_token_hash` exist
- [ ] **Verify:** Existing admin user can still log in with original credentials
- [ ] **Verify:** Admin user has `role=admin` and `is_active=true` in database

---

## 2. Backend API Checks

### Auth & Profile

- [ ] **Action:** `GET /api/auth/me` with valid admin token → **Expected:** 200 with `{ id, email, role: "admin", is_active, is_verified, created_at }`
- [ ] **Action:** `GET /api/auth/me` with no token → **Expected:** 401 Unauthorized
- [ ] **Action:** `GET /api/auth/me` with invalid token → **Expected:** 401 Unauthorized
- [ ] **Action:** Login as deactivated user → **Expected:** 401 with "deactivated" message

### User Management (Admin Only)

- [ ] **Action:** `GET /api/admin/users` as admin → **Expected:** 200 with list of all users including email, role, is_active, is_verified
- [ ] **Action:** `GET /api/admin/users` as editor → **Expected:** 403 Forbidden
- [ ] **Action:** `POST /api/admin/users/invite` as admin with `{ email, role }` → **Expected:** 200 with "invite sent" message
- [ ] **Action:** `POST /api/admin/users/invite` with duplicate email → **Expected:** 400 Bad Request
- [ ] **Action:** `POST /api/admin/users/invite` twice rapidly (same email) → **Expected:** Second returns 429 Too Many Requests
- [ ] **Action:** `PUT /api/admin/users/{id}/role` as admin with `{ role: "editor" }` → **Expected:** 200, user role updated
- [ ] **Action:** `PUT /api/admin/users/{id}/role` with invalid role → **Expected:** 400 Bad Request
- [ ] **Action:** `PUT /api/admin/users/{id}/active` as admin with `{ is_active: false }` → **Expected:** 200, user deactivated
- [ ] **Action:** `POST /api/auth/setup` with valid setup token → **Expected:** 200, user verified, password set
- [ ] **Action:** `POST /api/auth/setup` with same token again → **Expected:** 400 (single-use)
- [ ] **Action:** `POST /api/auth/setup` with expired token → **Expected:** 400

### Article Permissions

- [ ] **Action:** Contributor creates article → **Expected:** 201, article has contributor as author
- [ ] **Action:** Contributor edits own article → **Expected:** 200
- [ ] **Action:** Contributor edits another user's article → **Expected:** 403 Forbidden
- [ ] **Action:** Contributor publishes article → **Expected:** 403 Forbidden
- [ ] **Action:** Contributor deletes article → **Expected:** 403 Forbidden
- [ ] **Action:** Editor creates, edits, publishes, deletes any article → **Expected:** All 200/204
- [ ] **Action:** Admin creates, edits, publishes, deletes any article → **Expected:** All 200/204

### Article Reassignment (Admin Only)

- [ ] **Action:** `PUT /api/admin/articles/{id}/reassign` as admin with `{ author_id }` → **Expected:** 200, article author updated
- [ ] **Action:** Reassign as editor → **Expected:** 403 Forbidden
- [ ] **Action:** Reassign to inactive user → **Expected:** 400 Bad Request
- [ ] **Action:** Reassign to non-existent user → **Expected:** 400 Bad Request
- [ ] **Action:** Reassign with invalid UUID format → **Expected:** 400 Bad Request

### Revision History

- [ ] **Action:** `GET /api/admin/articles/{id}/revisions` → **Expected:** 200, each revision includes `author_email`
- [ ] **Action:** Save article → **Expected:** New revision with `change_type: "save"` and author email
- [ ] **Action:** Publish article → **Expected:** New revision with `change_type: "publish"` and author email
- [ ] **Action:** Restore revision → **Expected:** New revision with `change_type: "restore"` and author email
- [ ] **Action:** Reassign article → **Expected:** New revision with `change_type: "reassign"` and author email, `reassign_metadata` populated

---

## 3. Frontend UI Checks

### Login & Profile

- [ ] **Action:** Login with admin credentials → **Expected:** Redirects to /admin, profile loaded (check network tab for `/api/auth/me` call)
- [ ] **Action:** Refresh page while logged in → **Expected:** Stays logged in, profile restored from `/api/auth/me`
- [ ] **Action:** Login with deactivated account → **Expected:** Error message about deactivated account

### Admin Articles List

- [ ] **Action:** Navigate to /admin → **Expected:** Articles table shows "Author" column with email addresses
- [ ] **Action:** Create new article → **Expected:** Article appears with current user as author

### Article Edit View

- [ ] **Action:** Open article as contributor → **Expected:** Publish button hidden, Delete button hidden, no "Change Author" dropdown
- [ ] **Action:** Open article as editor → **Expected:** Publish button visible, Delete button visible, "Change Author" dropdown visible
- [ ] **Action:** Open article as admin → **Expected:** All buttons visible, "Change Author" dropdown visible
- [ ] **Action:** Change author as admin → **Expected:** Confirmation dialog, then success message, author updated
- [ ] **Action:** Auto-save as contributor on own article → **Expected:** Saves successfully
- [ ] **Action:** Auto-save as contributor on another's article → **Expected:** 403 error

### Revision History Panel

- [ ] **Action:** Open revision panel on any article → **Expected:** Each revision shows timestamp + author email
- [ ] **Action:** Restore a revision → **Expected:** Confirmation dialog, then article restored, new "restore" revision appears with author email

### Admin Users Page (Admin Only)

- [ ] **Action:** Navigate to /admin/users as admin → **Expected:** Users table with email, role, status, active toggle, joined date
- [ ] **Action:** Click "Invite User" → **Expected:** Modal opens with email input and role dropdown
- [ ] **Action:** Submit invite form with valid email → **Expected:** Success message, user appears in table
- [ ] **Action:** Submit invite with duplicate email → **Expected:** Error message "User already exists"
- [ ] **Action:** Change role via dropdown → **Expected:** Saves immediately, loading indicator during save
- [ ] **Action:** Toggle active off → **Expected:** Confirmation dialog, then user greyed out with "Inactive" badge
- [ ] **Action:** Navigate to /admin/users as editor → **Expected:** Redirected to /admin (no access)
- [ ] **Action:** Check sidebar → **Expected:** "Users" link visible for admin, hidden for editor/contributor

### Sidebar Navigation

- [ ] **Action:** Login as admin → **Expected:** Sidebar shows all links including "Users"
- [ ] **Action:** Login as editor → **Expected:** Sidebar shows all links except "Users"
- [ ] **Action:** Login as contributor → **Expected:** Sidebar shows all links except "Users"

---

## 4. Edge Cases & Error Handling

- [ ] **Action:** Contributor tries to access /admin/users directly → **Expected:** Redirected to /admin
- [ ] **Action:** Editor tries to access /admin/users directly → **Expected:** Redirected to /admin
- [ ] **Action:** Deactivated user tries to login → **Expected:** 401 with "deactivated" message
- [ ] **Action:** Deactivated user's articles on public site → **Expected:** Still visible and accessible
- [ ] **Action:** Invite user, then invite same email within 60 seconds → **Expected:** 429 rate limit
- [ ] **Action:** Setup with expired token (modify DB to set past expiry) → **Expected:** 400 error
- [ ] **Action:** Reassign article to self → **Expected:** 200 (allowed, no-op)
- [ ] **Action:** Import markdown file → **Expected:** Article created with importing user as author
- [ ] **Action:** Network failure during fetchMe → **Expected:** Token cleared, redirected to login
- [ ] **Action:** Invalid role value in API request → **Expected:** 400 Bad Request with validation error

---

## 5. Integration Checks

- [ ] **Action:** Invite user → Check email inbox for setup link → Click link → Set password → Login → **Expected:** User verified, role assigned, can access admin
- [ ] **Action:** Admin creates article → Editor edits and publishes → **Expected:** Article published, both users appear in revision history
- [ ] **Action:** Contributor creates draft → Editor publishes → **Expected:** Article published, newsletter sent (if enabled), both users in revision history
- [ ] **Action:** Admin reassigns article → Check revision history → **Expected:** "reassign" revision with old/new author metadata
- [ ] **Action:** Admin deactivates user → User tries to login → **Expected:** Blocked, existing articles still public
- [ ] **Action:** Refresh page with valid token → **Expected:** Profile restored via `/api/auth/me`, no redirect to login
- [ ] **Action:** Logout → **Expected:** Token cleared, user cleared, redirected to login
- [ ] **Action:** Create article → Check database → **Expected:** `author_id` populated with creator's user ID
- [ ] **Action:** Publish article → Check revision history → **Expected:** "publish" revision with author_id of publisher
