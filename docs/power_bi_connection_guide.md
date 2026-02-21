# Power BI Connection Guide

## Connecting Power BI to PostgreSQL

This guide shows how to connect the `uis_analytics` database to Power BI Desktop
for the OIRE dashboard.

### Prerequisites
- Power BI Desktop (free download from Microsoft)
- PostgreSQL ODBC driver
- `uis_analytics` database running on localhost or server

### Steps

1. **Open Power BI Desktop**
2. **Get Data** → **PostgreSQL Database**
3. **Server**: `localhost` (or your DB server address)
4. **Database**: `uis_analytics`
5. Click **OK**, then select tables:
   - `fact_enrollment`
   - `fact_retention_rates`
   - `fact_graduation_rates`
   - `vw_enrollment_summary` (pre-built view)
   - `vw_retention_dashboard` (pre-built view)

### Recommended Visuals

| Metric | Recommended Visual | Fields |
|--------|-------------------|--------|
| Enrollment trend | Line chart | year, total_enrollment |
| Retention by group | Multi-line | year, ft/pt/pell/firstgen retention |
| Peer comparison | Horizontal bar | institution, grad_rate_6yr |
| KPI summary | Card visuals | Latest year metrics |
| Equity gap | Stacked bar | year, pell vs non-pell retention |

### Refresh Schedule
- Set automatic refresh to run the ETL pipeline after IPEDS data releases
  (typically October for Fall data)
- IPEDS release schedule: https://nces.ed.gov/ipeds/use-the-data/survey-data-collection-schedule

### Notes
- Use the pre-built views (`vw_*`) for dashboard connections — they're optimized
- The `fact_il_benchmarks` table only has 2023 data currently; add prior years
  when doing multi-year benchmark trending
