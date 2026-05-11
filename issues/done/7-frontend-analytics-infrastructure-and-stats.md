## Parent

[PRD-subscriber-analytics.md](../prd/PRD-subscriber-analytics.md)

## What to build

Set up the frontend infrastructure for analytics. This involves installing charting dependencies and creating the layout for the Analytics dashboard with summary statistics.

## Acceptance criteria

- [ ] `chart.js` and `vue-chartjs` installed in the frontend.
- [ ] `AnalyticsView.vue` created and added to the admin router.
- [ ] "Analytics" link added to the admin sidebar.
- [ ] Time-range toggle (7d, 30d, 90d) implemented.
- [ ] Summary cards showing total active subscribers and period-over-period growth.

## Blocked by

- [6-backend-analytics-aggregation-api.md](./6-backend-analytics-aggregation-api.md)
