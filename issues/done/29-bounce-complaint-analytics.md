## Parent

PRD: Bounce Handling (prd/PRD-bounce-handling.md)

## What to build

Add bounce and complaint metrics to the analytics dashboard. Backend: add `total_bounces`, `total_complaints`, `bounce_rate`, and `complaint_rate` to the analytics summary. Add `bounces` and `complaints` to the growth time-series. Frontend: display bounce rate and complaint rate cards alongside existing open rate/CTR metrics in AdminAnalyticsView.

## Acceptance criteria

- [ ] Analytics endpoint returns `total_bounces`, `total_complaints`, `bounce_rate`, `complaint_rate` in summary
- [ ] Analytics endpoint returns `bounces` and `complaints` in growth time-series
- [ ] `bounce_rate = bounces / total_sent * 100`, `complaint_rate = complaints / total_sent * 100`
- [ ] AdminAnalyticsView displays bounce rate and complaint rate cards
- [ ] Test: analytics includes bounce/complaint metrics
- [ ] `just test` passes
- [ ] `cd frontend && npm run test` passes

## Blocked by

- #27-permanent-bounce-unsubscribe.md
- #28-complaint-unsubscribe.md
