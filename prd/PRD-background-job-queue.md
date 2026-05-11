## Problem Statement

Currently, the platform sends newsletters and confirmation emails synchronously during the HTTP request. As the subscriber list grows, this causes several critical issues:
1. **Timeouts:** HTTP requests may time out before all emails are sent.
2. **Reliability:** If the server crashes or an API error occurs mid-blast, there is no way to resume or retry failed sends without double-sending to others.
3. **UX:** The admin UI hangs while waiting for thousands of emails to be processed.
4. **Scale:** The current sequential loop cannot leverage multi-core processing or handle rate limits effectively.

## Solution

Implement a robust background job system using **Redis** and **ARQ**. This system will decouple email delivery from the API request lifecycle, allow for automatic retries, and provide real-time progress tracking of newsletter blasts. It also unlocks the ability to schedule newsletters for future delivery.

## User Stories

1. As an admin, I want to publish an article and have the newsletter blast handled in the background, so I can continue using the dashboard immediately.
2. As an admin, I want to see a progress bar or status indicator for an ongoing newsletter blast, so I know how many subscribers have received the update.
3. As a subscriber, I want to receive my confirmation email reliably, even if the email provider is temporarily down.
4. As an admin, I want to schedule a newsletter to be sent at a specific date and time in the future, so I can plan my content strategy.
5. As a developer, I want failed email jobs to automatically retry with exponential backoff, so that transient network issues don't result in missed deliveries.
6. As a developer, I want to distinguish between "permanent" failures (like invalid configuration) and "transient" failures (like rate limits), so I don't waste resources retrying hopeless tasks.

## Implementation Decisions

### 1. Stack & Infrastructure
- **Broker:** Redis 7 (alpine) added to `docker-compose.dev.yml` and `prod.yml`.
- **Worker:** A dedicated `worker` service in Docker running the ARQ worker.
- **Library:** `arq` for async-native job processing.

### 2. Job Pattern: Fan-out
- **Orchestrator Job (`blast_newsletter`)**: 
    - Queries all active subscribers.
    - Creates `NewsletterSend` records in the database with `status="pending"` (Intent-First pattern).
    - Enqueues individual `send_single_email` jobs for each subscriber.
- **Individual Task (`send_single_email`)**:
    - Fetches the subscriber and article from the DB.
    - Renders the TipTap content.
    - Calls the `EmailService`.
    - Updates the `NewsletterSend` record to `sent` or `failed`.

### 3. Model Changes (`NewsletterSend`)
- Add `status: str` (pending, sent, failed).
- Add `scheduled_at: Optional[datetime]`.
- Add `error_message: Optional[str]` to store failure reasons.

### 4. Retry Logic
- Configure ARQ with `max_tries=5` and exponential backoff.
- Workers will catch `EmailServiceError`. If the error is identified as "permanent" (e.g., domain verification issue), it will skip retries and mark as `failed`.

### 5. API & UI Integration
- The `publish` endpoint will no longer call the email loop directly; it will enqueue the orchestrator job.
- The `scheduled_at` field will be accepted by the API to support future delivery.

## Testing Decisions

- **Mocking Redis:** Use `arq.connections.MockRedis` or similar for unit tests to ensure jobs are enqueued correctly without needing a live Redis instance.
- **Orchestrator Tests:** Verify that for $N$ subscribers, $N$ `NewsletterSend` records are created and $N$ tasks are enqueued.
- **Worker Tests:** Verify the worker correctly handles `EmailServiceError` by updating the DB status to `failed`.
- **Concurrency Tests:** Ensure that the "Intent-First" pattern prevents race conditions.

## Out of Scope
- A full-featured analytics dashboard (this will be a separate PRD).
- Subscriber segmentation/tagging (separate PRD).
- Email open/click tracking webhooks.

## Further Notes
- The "Intent-First" database commitment ensures that if the orchestrator crashes, we have a record of who *should* have received the email, allowing for a recovery script or manual retry of the batch.
