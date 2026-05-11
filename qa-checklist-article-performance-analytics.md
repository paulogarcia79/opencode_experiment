# QA Checklist: Article Performance Analytics

## 1. Prerequisites & Setup

- [ ] Backend dev server running on `:8000`
- [ ] Frontend dev server running on `:5173`
- [ ] Admin user logged in (valid JWT token)
- [ ] At least 2 published articles exist (one with newsletter sent, one without)
- [ ] At least 1 draft article exists

## 2. Backend API Checks

### GET /api/articles/{slug} — View Tracking

- [ ] **Action:** Fetch a published article → **Expected:** 200, article data returned, view recorded in DB
- [ ] **Action:** Fetch the same published article again within 24h → **Expected:** 200, no duplicate view recorded
- [ ] **Action:** Fetch a draft article → **Expected:** 404, no view recorded

### GET /api/admin/articles/{id}/analytics — Per-Article Detail

- [ ] **Action:** GET with valid admin token and existing article ID → **Expected:** 200, JSON with `total_views`, `unique_views_24h`, `email_sent`, `email_opens`, `email_clicks`, `email_open_rate`, `email_ctr`
- [ ] **Action:** GET without auth token → **Expected:** 401 Unauthorized
- [ ] **Action:** GET with non-existent article ID → **Expected:** 404 Not Found
- [ ] **Action:** GET for article with no newsletter sends → **Expected:** email metrics all `0`, rates `0`

### GET /api/admin/articles/performance — List All Articles

- [ ] **Action:** GET with valid admin token → **Expected:** 200, array of all articles (draft + published) with performance metrics
- [ ] **Action:** GET without auth token → **Expected:** 401 Unauthorized
- [ ] **Action:** Verify draft articles in response have `total_views: 0` and `email_sent: 0` → **Expected:** correct

## 3. Frontend UI Checks

### Admin Articles List (`/admin`)

- [ ] **Action:** Navigate to `/admin` → **Expected:** Table shows "Views" and "Email CTR" columns between "Status" and "Published"
- [ ] **Action:** Check a published article with views → **Expected:** "Views" column shows number > 0
- [ ] **Action:** Check a published article with newsletter sends → **Expected:** "Email CTR" column shows percentage (e.g., "50.0%")
- [ ] **Action:** Check a draft article → **Expected:** "Views" shows `0`, "Email CTR" shows `—`
- [ ] **Action:** Verify column styling matches existing dark theme → **Expected:** Consistent font, colors, alignment

### Analytics Page (`/admin/analytics`)

- [ ] **Action:** Navigate to `/admin/analytics` → **Expected:** Existing charts load, plus new "Article Performance" section below
- [ ] **Action:** Check Article Performance table → **Expected:** Columns: Title (with status badge), Views, Unique (24h), Email Sent, Opens, Clicks, Open Rate, CTR
- [ ] **Action:** Verify articles sorted by views descending → **Expected:** Highest view count at top
- [ ] **Action:** Change time range toggle (7d / 30d / 90d) → **Expected:** Page reloads, article performance data updates
- [ ] **Action:** Verify table styling matches existing dark theme → **Expected:** Consistent with rest of analytics page

## 4. Edge Cases & Error Handling

- [ ] **Action:** Rapidly refresh a published article page 5+ times → **Expected:** View count increases by only 1 (24h dedup)
- [ ] **Action:** Access `/api/admin/articles/{id}/analytics` without being logged in → **Expected:** 401 error
- [ ] **Action:** Access `/api/admin/articles/performance` without being logged in → **Expected:** 401 error
- [ ] **Action:** View analytics for an article with zero views and zero sends → **Expected:** All metrics show `0`, rates show `0`
- [ ] **Action:** Navigate to `/admin/analytics` with no articles → **Expected:** "No articles yet" message in performance table

## 5. Integration Checks

- [ ] **Action:** Publish a new draft article → visit it on public site → check admin articles list → **Expected:** Views column increments to 1
- [ ] **Action:** Publish article with newsletter → wait for sends → check analytics page → **Expected:** Email metrics reflect actual sends/opens/clicks
- [ ] **Action:** Visit same article from different browser/incognito → check analytics page → **Expected:** Unique views increments (different IP hash)
- [ ] **Action:** Delete an article → verify its performance data is also removed (cascade) → **Expected:** No orphaned `ArticleView` records
