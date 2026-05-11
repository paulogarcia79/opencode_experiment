## Parent

[PRD-email-tracking.md](../prd/PRD-email-tracking.md)

## What to build

Enhance the analytics API to include engagement metrics. The backend should calculate aggregate open rates and click-through rates based on the tracking data captured from webhooks.

## Acceptance criteria

- [ ] `GET /api/admin/analytics` updated to return `total_opens`, `total_clicks`, `open_rate`, and `ctr`.
- [ ] Logic accounts for multiple opens/clicks per recipient (distinct vs total counts).
- [ ] Unit tests verify the accuracy of rate calculations across different time ranges.

## Blocked by

- [14-tracking-schema-and-webhook-infrastructure.md](./14-tracking-schema-and-webhook-infrastructure.md)
