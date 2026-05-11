## Parent

[PRD-background-job-queue.md](../prd/PRD-background-job-queue.md)

## What to build

Enable admins to schedule newsletters for future delivery using ARQ's scheduling capabilities.

## Acceptance criteria

- [ ] Article model and API updated to support a `scheduled_for` timestamp.
- [ ] When an article is published with a `scheduled_for` time, the `blast_newsletter` job is enqueued with `defer_until`.
- [ ] Integration tests verify that the orchestrator job is delayed until the specified time.

## Blocked by

- [3-newsletter-fan-out-and-orchestration.md](./3-newsletter-fan-out-and-orchestration.md)
