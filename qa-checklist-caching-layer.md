# QA Checklist: Caching Layer

This checklist verifies the end-to-end functionality of the Redis caching layer, decoupled view tracking, and decoupled admin previews.

## 1. Prerequisites & Setup

- [ ] **Action:** Ensure Docker is running with PostgreSQL and Redis (e.g., `just db` or using docker-compose).
- [ ] **Action:** Start the backend server locally with `just back`.
- [ ] **Action:** Start the frontend server locally with `just front`.
- [ ] **Action:** Log in as an admin or editor.
- [ ] **Action:** Create a published article (e.g., "Cache Test Article") and an unpublished draft (e.g., "Secret Draft").

## 2. Admin Preview Decoupling (Frontend & Backend)

- [ ] **Action:** As an admin, go to the Articles list (`/admin`) and click "View" on "Secret Draft". → **Expected:** You are taken to `/articles/secret-draft?preview=true` and the article renders successfully.
- [ ] **Action:** Open an incognito window (unauthenticated) and navigate directly to `/articles/secret-draft` (without the `?preview=true`). → **Expected:** The page shows a 404 "Error loading article / Article not found".
- [ ] **Action:** In the incognito window, navigate to `/api/articles/secret-draft` directly in the browser address bar. → **Expected:** Returns a 404 JSON response.
- [ ] **Action:** In the incognito window, navigate to `/api/admin/articles/preview/secret-draft`. → **Expected:** Returns a 401 Unauthorized JSON response.

## 3. Client-Side View Tracking

- [ ] **Action:** Open an incognito window (unauthenticated) and navigate to the published "Cache Test Article". Wait for the page to load completely.
- [ ] **Action:** Open the Network tab in Developer Tools. → **Expected:** You should see a background `POST` request to `/api/articles/cache-test-article/view` that returns a 200 OK.
- [ ] **Action:** As an admin, check the Analytics dashboard or the Performance list for "Cache Test Article". → **Expected:** The view count should have increased by 1.
- [ ] **Action:** In the incognito window, reload the same article. Check the Analytics again. → **Expected:** The view count should **not** increase (due to the 24h IP deduplication rule, which should still be functioning correctly).

## 4. Redis Caching Layer Performance

- [ ] **Action:** Open the Network tab in Developer Tools and reload the public homepage `/`. Look at the request for `/api/articles`. → **Expected:** The response time should be significantly faster on the second load compared to the first.
- [ ] **Action:** Navigate to the published "Cache Test Article" and check its API response time. → **Expected:** The response time for `/api/articles/cache-test-article` should be extremely fast (cached).
- [ ] **Action:** Open `/feed.xml` in the browser and refresh. → **Expected:** The response time should be extremely fast.

## 5. Cache Invalidation (Event-Driven)

- [ ] **Action:** As an admin, edit "Cache Test Article", change the title to "Cache Test Article Updated", and click "Update Article".
- [ ] **Action:** Open an incognito window and go to the homepage `/`. → **Expected:** The article title should immediately show "Cache Test Article Updated" (the cache was invalidated on update).
- [ ] **Action:** Click into the article. → **Expected:** The article content/title should be updated immediately.
- [ ] **Action:** Open `/feed.xml`. → **Expected:** The new title should appear in the XML immediately.
- [ ] **Action:** Create a completely new published article via the admin dashboard. Check the homepage. → **Expected:** The new article appears instantly.
- [ ] **Action:** Delete an article via the admin dashboard. Check the homepage. → **Expected:** The article is removed instantly.