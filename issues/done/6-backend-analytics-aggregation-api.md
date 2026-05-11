## Parent

[PRD-subscriber-analytics.md](../prd/PRD-subscriber-analytics.md)

## What to build

Implement the backend logic to aggregate subscriber and newsletter delivery data. This includes creating a new endpoint that performs SQL groupings by date to return time-series data for the dashboard.

## Acceptance criteria

- [ ] New endpoint `GET /api/admin/analytics` implemented.
- [ ] Endpoint accepts a `range` parameter (7d, 30d, 90d).
- [ ] Returns daily/weekly counts of signups and unsubscribes.
- [ ] Returns aggregate counts of `sent` and `failed` newsletter sends.
- [ ] Endpoint is protected by `require_admin`.
- [ ] Unit tests verify correct SQL aggregation (handling SQLite vs PostgreSQL date functions if necessary).

## Blocked by

None - can start immediately
