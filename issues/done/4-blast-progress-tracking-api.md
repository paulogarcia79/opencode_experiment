## Parent

[PRD-background-job-queue.md](../prd/PRD-background-job-queue.md)

## What to build

Expose the progress of ongoing newsletter blasts via a new API endpoint. This allows the frontend to show real-time feedback to admins.

## Acceptance criteria

- [ ] New endpoint `GET /api/admin/newsletter-blasts/{article_id}/status` implemented.
- [ ] Response includes counts of `pending`, `sent`, and `failed` records for the specific article.
- [ ] Includes a derived `progress_percentage`.
- [ ] Endpoint requires admin authentication.

## Blocked by

- [3-newsletter-fan-out-and-orchestration.md](./3-newsletter-fan-out-and-orchestration.md)
