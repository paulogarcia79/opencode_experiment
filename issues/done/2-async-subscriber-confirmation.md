## Parent

[PRD-background-job-queue.md](../prd/PRD-background-job-queue.md)

## What to build

Offload the subscriber confirmation email to a background task. When a user subscribes, the API should enqueue a job instead of sending the email synchronously.

## Acceptance criteria

- [ ] ARQ worker process defined and integrated into `docker-compose.dev.yml` as a separate service.
- [ ] `send_confirmation_email_task` implemented in a new `app/worker.py`.
- [ ] `subscribe_endpoint` updated to enqueue the confirmation email job via ARQ.
- [ ] Tests verify that the job is enqueued with the correct arguments when the endpoint is called.
- [ ] Worker successfully processes the job and sends the email (verified via logs/mock).

## Blocked by

- [1-infrastructure-and-model-evolution.md](./1-infrastructure-and-model-evolution.md)
