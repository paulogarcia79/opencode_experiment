## Parent

[PRD-background-job-queue.md](../prd/PRD-background-job-queue.md)

## What to build

Implement the "Fan-out" pattern for newsletter delivery. The publishing process should trigger an orchestrator job that prepares the database records and enqueues individual email tasks.

## Acceptance criteria

- [ ] `blast_newsletter` orchestrator job implemented:
    - Creates `pending` `NewsletterSend` records for all active subscribers.
    - Enqueues individual `send_single_email` tasks.
- [ ] `send_single_email` task implemented:
    - Renders article content.
    - Updates `NewsletterSend` status to `sent` or `failed` (with `error_message`).
- [ ] Publish article endpoint updated to enqueue the `blast_newsletter` job.
- [ ] Logic implemented to distinguish between transient (retryable) and permanent (fatal) email errors.

## Blocked by

- [1-infrastructure-and-model-evolution.md](./1-infrastructure-and-model-evolution.md)
