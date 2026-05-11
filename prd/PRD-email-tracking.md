# PRD: Email Open/Click Tracking

## Problem Statement
The blog administrator can currently see how many newsletters were "sent" or "failed" through the Analytics Dashboard, but they have no visibility into recipient engagement. There is no way to know if emails are actually being opened or if links are being clicked. This makes it impossible to measure content effectiveness or identify deliverability issues (e.g., emails landing in spam).

## Solution
Integrate **Resend Webhooks** to track email engagement events (opens and clicks) in real-time. Update the backend to process these webhooks and store the results in the database, then enhance the Analytics Dashboard to display **Open Rates** and **Click-Through Rates (CTR)**.

## User Stories
1. As an admin, I want to see the total number of opens for each newsletter, so that I can understand how many people are reading my content.
2. As an admin, I want to see which links in my newsletter are clicked the most, so that I can identify the most engaging topics.
3. As an admin, I want to see an "Open Rate" percentage on my dashboard, so that I can track audience engagement trends over time.
4. As a developer, I want a secure webhook endpoint to receive events from Resend, so that engagement data is automatically synchronized with our database.
5. As an admin, I want to see if an email was "Bounced", so that I can monitor the health of my subscriber list and identify invalid addresses.

## Implementation Decisions

### 1. Database Schema Changes
- **`NewsletterSend` Model**: 
    - Add `opened_at: Optional[datetime]` (tracks first open).
    - Add `clicked_at: Optional[datetime]` (tracks first click).
    - Add `open_count: int` (tracks total number of opens).
    - Add `click_count: int` (tracks total number of clicks).
- **`EmailEvent` Model (New)**:
    - Stores raw event data from webhooks for auditing/debugging.
    - Fields: `id`, `newsletter_send_id`, `event_type` (open, click, bounce), `timestamp`, `raw_payload`.

### 2. Webhook Endpoint (`app/routers/webhooks.py`)
- **Endpoint**: `POST /api/webhooks/resend`.
- **Security**: Implement webhook signature verification (if supported by Resend/requested) or a secret token in the URL.
- **Logic**: Match the Resend `email_id` or a custom metadata ID (passed during send) to the corresponding `NewsletterSend` record and update its engagement stats.

### 3. Email Service Integration
- Update `send_newsletter_email` in `app/services/email_service.py` to include a unique identifier in the Resend `headers` or `tags` so that events can be traced back to the correct `NewsletterSend` record.

### 4. Analytics API & UI Updates
- **Backend**: Update `GET /api/admin/analytics` to include:
    - Aggregate Open Rate (Total Opens / Total Sent).
    - Aggregate CTR (Total Clicks / Total Sent).
- **Frontend**: Add new summary cards and charts for Open/Click performance on the Analytics page.

## Testing Decisions
- **Webhook Processing Tests**: Mock Resend webhook payloads and verify that the corresponding database records are updated correctly.
- **Traceability Tests**: Ensure that the unique ID passed to Resend during sending is correctly returned in the webhook events.
- **Analytics Integrity**: Verify that Open Rates and CTR are calculated correctly even when some emails fail or bounce.

## Out of Scope
- Real-time "Live Feed" of opens/clicks (dashboard will reflect data on refresh).
- Deep link-level analytics (tracking *which specific URL* was clicked; initially we will track *if any* link was clicked).
- Automatic purging of bounced subscribers (this is a separate "Bounce Handling" feature).

## Further Notes
- Resend provides `open` and `click` tracking out of the box when enabled in their dashboard or via API parameters. We will ensure it is enabled in our API calls.
