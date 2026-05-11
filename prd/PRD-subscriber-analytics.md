# PRD: Subscriber Analytics Dashboard

## Problem Statement
The blog administrator currently has no visibility into audience growth or newsletter performance. While we have the data stored in the database, there is no way to visualize trends over time (growth vs. churn) or monitor the health of the background delivery system. This makes it difficult to assess the impact of new content or identify delivery issues.

## Solution
Implement a dedicated **Analytics Dashboard** in the admin area. This dashboard will provide a centralized view of key audience metrics and delivery performance using interactive charts and summary statistics. Data will be aggregated on-the-fly from existing tables to ensure real-time accuracy.

## User Stories
1. As an admin, I want to see a chart of new subscribers over time, so I can see which articles drive the most signups.
2. As an admin, I want to toggle between different time ranges (7 days, 30 days, 90 days), so I can analyze both short-term impact and long-term trends.
3. As an admin, I want to see the total count of active, pending, and unsubscribed users, so I know the current size of my reachable audience.
4. As an admin, I want to see the delivery success rate of recent newsletters, so I can verify that the background worker and email provider are functioning correctly.
5. As an admin, I want to see a "churn" metric (unsubscribes over time), so I can understand if my content is retaining or losing readers.

## Implementation Decisions

### 1. Backend Analytics API
- **Endpoint**: `GET /api/admin/analytics`
- **Params**: `range` (7d, 30d, 90d)
- **Logic**: Use SQL `date_trunc` or `strftime` (for SQLite tests) and `GROUP BY` to aggregate:
    - Daily/Weekly subscriber signups.
    - Daily/Weekly unsubscribes.
    - Aggregate delivery stats from `NewsletterSend` (sent vs. failed).
- **Auth**: Protected by the existing `require_admin` dependency.

### 2. Frontend Visualization
- **Library**: `chart.js` and `vue-chartjs`.
- **Components**:
    - **Summary Cards**: Large numbers for Total Active, Growth % this period, and Overall Delivery Rate.
    - **Growth Chart**: A line chart showing new signups vs. unsubscribes over the selected timeframe.
    - **Delivery Chart**: A doughnut or bar chart showing successful vs. failed sends for the most recent newsletter blasts.
- **Navigation**: Add an "Analytics" link to the Admin Sidebar.

### 3. Data Strategy
- **On-the-fly Aggregation**: Queries will run directly against the `subscribers` and `newsletter_sends` tables. No materialized views or summary tables are needed at this stage.

## Testing Decisions
- **Backend**: Integration tests will populate the database with subscribers across different dates and verify that the `analytics` endpoint returns correctly bucketed data.
- **Frontend**: Unit tests for the Analytics view to ensure time-range toggles correctly trigger new API calls.

## Out of Scope
- Per-article open/click rate tracking (requires Resend webhook integration, which is a future item).
- Geography/location data of subscribers.
- Exporting data to CSV/Excel.

## Further Notes
- The "lab aesthetic" of the dashboard should match the existing dark tech theme (Space Grotesk font, Inter for numbers, emerald/primary accents).
