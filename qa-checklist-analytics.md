# QA Checklist: Subscriber Analytics Dashboard

Manual verification steps for the Subscriber Analytics Dashboard, including backend data aggregation and frontend visualizations.

## 1. Prerequisites & Setup
- [ ] **Action:** Run `docker ps` → **Expected:** All services (`db`, `redis`, `backend`, `worker`, `frontend`, `nginx`) are running.
- [ ] **Action:** Log in as an admin at `/admin/login`.
- [ ] **Action:** Ensure there are some subscribers (active and unsubscribed) and recent newsletter sends in the database.

## 2. Backend API Checks
- [ ] **Action:** GET `/api/admin/analytics?range=30d` (using browser/curl with JWT) → **Expected:** Returns `200 OK` with JSON containing `summary`, `growth` (signups/unsubscribes list), and `delivery` (sent/failed/pending) objects.
- [ ] **Action:** GET `/api/admin/analytics?range=invalid` → **Expected:** Returns `422 Unprocessable Entity` (due to Pydantic Query pattern validation).

## 3. Frontend UI Checks
- [ ] **Action:** Click "Analytics" in the admin sidebar → **Expected:** Navigates to `/admin/analytics` and displays the dashboard.
- [ ] **Action:** Observe the Summary Cards → **Expected:** "Active Subscribers", "Pending", and "Total Unsubscribed" show correct counts corresponding to the database.
- [ ] **Action:** Observe the "Growth Over Time" chart → **Expected:** Shows a line chart with emerald (Signups) and rose (Unsubscribes) lines.
- [ ] **Action:** Observe the "Newsletter Delivery" chart → **Expected:** Shows a doughnut chart representing Sent, Failed, and Pending jobs.
- [ ] **Action:** Click the "7 Days", "30 Days", and "90 Days" toggles → **Expected:** Dashboard shows a loading spinner, then updates charts and "this period" badges with data for the selected range.

## 4. Edge Cases & Error Handling
- [ ] **Action:** Access `/admin/analytics` while logged out → **Expected:** Redirects to `/admin/login`.
- [ ] **Action:** Test on a fresh database with zero subscribers → **Expected:** Dashboard loads correctly showing "0" for all stats and empty charts (or zero-baseline lines) without crashing.
- [ ] **Action:** Hover over data points in the Growth Chart → **Expected:** Tooltip appears showing the exact count for that specific date.

## 5. Integration Checks
- [ ] **Action:** Sign up a new subscriber on the public site and confirm them, then refresh the Analytics dashboard → **Expected:** "Active Subscribers" count increases by 1, and the Growth Chart shows a new data point for today.
- [ ] **Action:** Trigger a newsletter blast (Publish article), wait for it to complete, then refresh Analytics → **Expected:** "Newsletter Delivery" doughnut chart updates to reflect the new successful/failed sends.
