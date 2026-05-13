## 1. Prerequisites & Setup

- [ ] Full stack running: `just dev`
- [ ] At least one user of each role in the database (admin, editor, contributor)
- [ ] Multiple articles exist: some drafts, some published, some belonging to different authors
- [ ] JWT tokens available for each role (log in to obtain)

## 2. Backend API Checks

### 2.1 Article Model & Statuses

- [ ] `POST /api/admin/articles` with `status: "pending_review"` in JSON body → **Expected:** article created, status visible in response
- [ ] `GET /api/admin/articles?status=pending_review` → **Expected:** only articles with `pending_review` status returned
- [ ] `GET /api/admin/articles?sort=title&order=asc` → **Expected:** articles sorted alphabetically by title
- [ ] `GET /api/admin/articles?sort=invalid_column` → **Expected:** 400 Bad Request
- [ ] `GET /api/admin/articles?sort=title&order=invalid` → **Expected:** 400 Bad Request

### 2.2 Role Scoping

- [ ] **As contributor** `GET /api/admin/articles` → **Expected:** only contributor's own articles returned
- [ ] **As editor** `GET /api/admin/articles` → **Expected:** all articles returned (no filter)
- [ ] **As admin** `GET /api/admin/articles` → **Expected:** all articles returned
- [ ] **As contributor** `GET /api/admin/articles/{id}` for another user's article → **Expected:** 404 Not Found
- [ ] **As editor** `GET /api/admin/articles/{id}` for another user's article → **Expected:** 200 with article data

### 2.3 Endpoint Tightening

- [ ] **As editor** `GET /api/admin/analytics` → **Expected:** 403 Forbidden
- [ ] **As contributor** `GET /api/admin/analytics` → **Expected:** 403 Forbidden
- [ ] **As editor** `GET /api/admin/articles/performance` → **Expected:** 403 Forbidden
- [ ] **As contributor** `GET /api/admin/newsletter-blasts/{id}/status` → **Expected:** 403 Forbidden

### 2.4 Review Workflow

- [ ] **As contributor** `POST /api/admin/articles/{id}/submit-review` on own article → **Expected:** 200, `status: "pending_review"`, `submitted_at` not null
- [ ] **As contributor** `POST /api/admin/articles/{id}/submit-review` on another's article → **Expected:** 403 Forbidden
- [ ] **As editor** `POST /api/admin/articles/{id}/approve` on `pending_review` article → **Expected:** 200, `status: "published"`, `submitted_at: null`
- [ ] **As contributor** `POST /api/admin/articles/{id}/approve` → **Expected:** 403 Forbidden
- [ ] **As editor** `POST /api/admin/articles/{id}/reject` with `{"feedback": "Needs work"}` → **Expected:** 200, `status: "draft"`, `submitted_at: null`
- [ ] `GET /api/admin/articles/review` **as editor** → **Expected:** 200, only `pending_review` articles, includes author email and `submitted_at`
- [ ] `GET /api/admin/articles/review/count` **as editor** → **Expected:** 200, `{"pending_count": N}` where N matches actual count
- [ ] `GET /api/admin/articles/review/count` **as contributor** → **Expected:** 403 Forbidden

### 2.5 ReviewAction Records

- [ ] After approving: query `review_actions` table → **Expected:** new record with `action: "approved"`, `reviewer_id` matches approver
- [ ] After rejecting: query `review_actions` table → **Expected:** new record with `action: "rejected"`, `feedback` matches submitted text
- [ ] Reject same article twice → **Expected:** two separate `ReviewAction` records preserved

### 2.6 Contributor Delete

- [ ] **As contributor** `DELETE /api/articles/{id}` on own article → **Expected:** 204, article deleted
- [ ] **As contributor** `DELETE /api/articles/{id}` on another's article → **Expected:** 403 Forbidden

### 2.7 Public API Boundaries

- [ ] `GET /api/articles` → **Expected:** only `published` articles returned, no `draft` or `pending_review`
- [ ] `GET /api/articles/{slug}` for a `pending_review` article → **Expected:** 404 Not Found

## 3. Frontend UI Checks

### 3.1 Login & Routing

- [ ] Navigate to `/admin/login` → **Expected:** login form visible
- [ ] **As admin** log in → **Expected:** redirected to `/admin`
- [ ] **As editor** log in → **Expected:** redirected to `/editor`
- [ ] **As contributor** log in → **Expected:** redirected to `/contributor`

### 3.2 Route Guards

- [ ] **As editor** visit `/admin` → **Expected:** redirected to `/forbidden` with "403 — You don't have access"
- [ ] On forbidden page → **Expected:** "Back to Dashboard" link points to editor's dashboard (`/editor`)
- [ ] **As contributor** visit `/editor` → **Expected:** redirected to `/forbidden`
- [ ] **As contributor** visit `/admin/users` → **Expected:** redirected to `/forbidden`

### 3.3 Admin Dashboard Navigation

- [ ] **As admin** at `/admin` → **Expected:** nav shows: Articles, Review, Import, Media, Tags, Analytics, Settings, Users
- [ ] Review badge shows pending count (if any pending reviews)
- [ ] "View Site" link navigates to `/`
- [ ] Logout button clears session and redirects to `/admin/login`

### 3.4 Editor Dashboard Navigation

- [ ] **As editor** at `/editor` → **Expected:** nav shows: Articles, Review, Import, Settings
- [ ] **Expected:** no Users, Media, Tags, Analytics nav items visible
- [ ] Review badge shows pending count

### 3.5 Contributor Dashboard Navigation

- [ ] **As contributor** at `/contributor` → **Expected:** nav shows: Articles, Import, Settings
- [ ] **Expected:** no Review, Users, Media, Tags, Analytics nav items

### 3.6 Admin Articles Table (Expandable)

- [ ] **As admin** at `/admin` → **Expected:** articles table with Title, Author, Status columns + Actions
- [ ] Click any row → **Expected:** sub-row expands with detail card (Published date, Views, Email CTR)
- [ ] Click same row again → **Expected:** row collapses
- [ ] Click multiple rows → **Expected:** all stay expanded simultaneously
- [ ] **Expected:** no "Slug" column visible
- [ ] Edit button visible on all rows as admin → **Expected:** links to `/admin/articles/{id}/edit`
- [ ] Delete button visible on all rows as admin

### 3.7 Filter Tabs & Sort (Admin/Editor)

- [ ] Click "Drafts" tab → **Expected:** URL updates to `?status=draft`, table shows only drafts
- [ ] Click "Published" tab → **Expected:** URL updates to `?status=published`, only published shown
- [ ] Click "Pending Review" tab → **Expected:** only `pending_review` articles shown
- [ ] Click "All" tab → **Expected:** URL has no `status` param, all articles shown
- [ ] Click "Title" column header → **Expected:** rows sort alphabetically, URL gets `?sort=title&order=asc`
- [ ] Click "Title" again → **Expected:** sort reverses to desc
- [ ] Click "Status" column header → **Expected:** URL gets `?sort=status`

### 3.8 Infinite Scroll (Admin/Editor)

- [ ] Have 20+ articles → scroll to bottom → **Expected:** "Load More" button appears
- [ ] Click "Load More" → **Expected:** next 20 articles load, button disappears if no more
- [ ] Filter changes → **Expected:** articles reload from start (reset)

### 3.9 Contributor Card Dashboard

- [ ] **As contributor** at `/contributor` → **Expected:** card grid (3 per row on desktop), only own articles
- [ ] Each card shows: title, status badge, published date (or "—"), view count, Edit + Delete buttons
- [ ] Status badge colors: draft=gray, published=green, pending_review=red/pink
- [ ] Edit button → **Expected:** links to `/contributor/articles/{id}/edit`
- [ ] Delete button → **Expected:** confirmation dialog, article removed on confirm
- [ ] "Attention" badge shows count of rejected articles

### 3.10 Contributor Card Filter & Search

- [ ] Click "Drafts" tab → **Expected:** only drafts shown, URL `?status=draft`
- [ ] Click "Published" tab → **Expected:** only published shown
- [ ] Type in search box → **Expected:** debounced fetch, URL `?search=term`
- [ ] "Load More" button at bottom when 20+ articles

### 3.11 Review Queue Page

- [ ] **As editor** navigate to `/editor/review` → **Expected:** table of `pending_review` articles
- [ ] Table shows: Title, Author, Submitted Date, Approve + Reject buttons per row
- [ ] Expand row → **Expected:** shows article description (if any), previous rejection feedback (if any)
- [ ] Expanded row has "Open in full editor" link → **Expected:** links to `/editor/articles/{id}/edit`
- [ ] Empty state when no pending reviews → **Expected:** "No articles pending review"

### 3.12 Approve Flow

- [ ] Click "Approve" → **Expected:** confirmation dialog with article title, author, submitted date
- [ ] Click "Cancel" in dialog → **Expected:** dialog closes, nothing changes
- [ ] Click "Approve" in dialog → **Expected:** article removed from queue, status now published (verify in articles table)

### 3.13 Reject Flow

- [ ] Click "Reject" → **Expected:** modal opens with textarea for feedback
- [ ] Leave feedback empty, click "Reject" → **Expected:** button disabled
- [ ] Type feedback, click "Reject" → **Expected:** article removed from queue, status now draft
- [ ] Rejected article visible in contributor's cards with "Rejected" badge

### 3.14 Article Editor — Contributor Adaptations

- [ ] **As contributor** create new article → **Expected:** "Submit for Review" button in toolbar, NO publish toggle
- [ ] **Expected:** read-only status badge showing current status ("draft" initially)
- [ ] Click "Submit for Review" → **Expected:** status changes to `pending_review`, button changes to "Update Review"
- [ ] **As contributor** open a rejected article → **Expected:** rejection feedback banner at top, "Re-submit for Review" button
- [ ] Edit content + autosave on a `pending_review` article → **Expected:** status reverts to draft
- [ ] After autosave creates placeholder article, redirect → **Expected:** URL uses `/contributor/articles/{id}/edit`

### 3.15 Article Editor — Admin/Editor

- [ ] **As editor** open article → **Expected:** "Publish immediately" toggle visible
- [ ] Toggle to published → **Expected:** "Send newsletter" checkbox appears
- [ ] **As admin** open article in edit mode → **Expected:** "Change Author" dropdown visible

## 4. Edge Cases & Error Handling

### 4.1 Unauthorized Access

- [ ] Visit `/editor` without login → **Expected:** redirected to `/admin/login`
- [ ] Visit `/contributor/articles/new` without login → **Expected:** redirected to `/admin/login`
- [ ] **As editor** visit `/contributor/articles/{id}/edit` → **Expected:** redirected to `/editor/articles/{id}/edit`
- [ ] **As contributor** visit `/admin` → **Expected:** redirected to `/forbidden`
- [ ] Expired/invalid token → **Expected:** redirected to `/admin/login` on any protected route

### 4.2 Empty Data States

- [ ] Admin with zero articles → **Expected:** "No items to display" in table
- [ ] Contributor with zero articles → **Expected:** "No articles yet" with create prompt
- [ ] Editor opens review queue with zero pending → **Expected:** "No articles pending review"

### 4.3 Network & API Failures

- [ ] API returns 500 on article fetch → **Expected:** "Failed to load articles" error state visible
- [ ] API returns 500 on approve → **Expected:** alert with error message, article stays in queue
- [ ] API returns 500 on reject → **Expected:** alert with error message, article stays in queue

### 4.4 Invalid Inputs

- [ ] Submit empty feedback on reject → **Expected:** "Reject" button disabled
- [ ] Search for non-existent title → **Expected:** empty results
- [ ] Filter by status with no matching articles → **Expected:** empty table/cards

### 4.5 Concurrent Actions

- [ ] Two editors open same article in review queue → **Expected:** approve by first removes it; second gets API error

## 5. Integration Checks

### 5.1 Full Review Lifecycle

- [ ] Contributor creates article → **Expected:** status "draft"
- [ ] Contributor clicks "Submit for Review" → **Expected:** article appears in editor's review queue
- [ ] Editor rejects with feedback → **Expected:** article status "draft", contributor sees rejection banner + badge
- [ ] Contributor re-submits → **Expected:** article back in review queue, "Update Review" button
- [ ] Editor approves → **Expected:** article published, visible in public `/` route
- [ ] Public article list → **Expected:** approved article appears

### 5.2 Cross-Role Permissions

- [ ] Admin can edit any article → **Expected:** Edit button visible on all rows
- [ ] Editor can edit any article → **Expected:** Edit button visible on all rows
- [ ] Contributor can only edit own articles → **Expected:** Edit/Delete visible on own cards only
- [ ] Contributor can delete own articles → **Expected:** delete succeeds
- [ ] Contributor cannot delete others' articles → **Expected:** 403 from API

### 5.3 Namespace Isolation

- [ ] Admin creates article → **Expected:** edit URL is `/admin/articles/{id}/edit`
- [ ] Editor creates article → **Expected:** edit URL is `/editor/articles/{id}/edit`
- [ ] Contributor creates article → **Expected:** edit URL is `/contributor/articles/{id}/edit`
- [ ] Admin logs out, editor logs in → **Expected:** editor cannot access `/admin`
- [ ] Contributor logs out, admin logs in → **Expected:** admin can access all areas
