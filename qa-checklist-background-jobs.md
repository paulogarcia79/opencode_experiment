# QA Checklist: Background Job Queue (Redis + ARQ)

Manual verification steps for the Redis-backed background job system, covering subscriber confirmation, newsletter fan-out, tracking, and scheduling.

## 1. Prerequisites & Setup
- [ ] **Action:** Run `docker ps` → **Expected:** Services `db`, `redis`, `backend`, `worker`, and `frontend` are all running.
- [ ] **Action:** Ensure `RESEND_FROM_EMAIL` in `.env` is set to `onboarding@resend.dev` (or a verified domain).
- [ ] **Action:** Have at least one active subscriber in the database.

## 2. Backend API Checks

### Subscriber Confirmation
- [ ] **Action:** POST `/api/subscribers` with `{"email": "your-email@example.com"}` → **Expected:** Returns `200 OK`, message "Check your email", and worker logs show `send_confirmation_email_task` started.

### Newsletter Blast Progress
- [ ] **Action:** GET `/api/admin/newsletter-blasts/{article_id}/status` (as Admin) → **Expected:** Returns `200 OK` with JSON containing `pending`, `sent`, `failed`, `total`, and `progress_percentage`.

### Article Publishing & Scheduling
- [ ] **Action:** PUT `/api/articles/{article_id}` with `{"status": "published", "send_newsletter": true}` → **Expected:** Returns `200 OK`, worker logs show `blast_newsletter_task` followed by `send_single_email_task` for each active subscriber.
- [ ] **Action:** PUT `/api/articles/{article_id}` with `{"status": "published", "send_newsletter": true, "scheduled_for": "2026-12-31T10:00:00Z"}` → **Expected:** Returns `200 OK`, worker logs show job enqueued but *not* executed until the scheduled time.

## 3. Edge Cases & Error Handling
- [ ] **Action:** Trigger a newsletter blast with an invalid Resend API key → **Expected:** Progress API shows incrementing `failed` count; `error_message` in database (via psql) contains the Resend error.
- [ ] **Action:** Publish an article with `send_newsletter: false` → **Expected:** No `blast_newsletter_task` appears in worker logs.
- [ ] **Action:** Attempt to access `/api/admin/newsletter-blasts/{id}/status` without a valid JWT → **Expected:** Returns `401 Unauthorized`.

## 4. Integration Checks
- [ ] **Action:** Subscribe a new user, then immediately check database `subscribers` table → **Expected:** User appears with `status="pending"`. Wait 5 seconds → **Expected:** Confirmation email received (if using verified recipient).
- [ ] **Action:** Publish an article to 3+ subscribers while watching worker logs → **Expected:** Tasks executed in order: 1x `blast_newsletter_task`, then 3x `send_single_email_task`.
- [ ] **Action:** Verify idempotency: Manually restart worker mid-blast → **Expected:** Worker resumes and does not send duplicate emails to subscribers already marked `sent`.
