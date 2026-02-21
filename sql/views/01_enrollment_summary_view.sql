-- ============================================================
-- View: vw_enrollment_summary
-- Purpose: Pre-built summary for Power BI / Tableau connections
-- Author: Rakesh Budige
-- ============================================================

CREATE OR REPLACE VIEW vw_enrollment_summary AS
SELECT
    e.year,
    e.total_enrollment,
    e.undergrad_enrollment,
    e.grad_enrollment,
    e.full_time,
    e.part_time,
    e.online_only,
    ROUND(e.full_time::DECIMAL / e.total_enrollment * 100, 1) AS full_time_pct,
    ROUND(e.online_only::DECIMAL / e.total_enrollment * 100, 1) AS online_pct,
    ROUND(e.female::DECIMAL / e.total_enrollment * 100, 1) AS female_pct,
    ROUND((e.black + e.hispanic)::DECIMAL / e.total_enrollment * 100, 1) AS black_hispanic_pct,
    LAG(e.total_enrollment) OVER (ORDER BY e.year) AS prev_year_enrollment,
    e.total_enrollment - LAG(e.total_enrollment) OVER (ORDER BY e.year) AS yoy_change
FROM fact_enrollment e
WHERE e.unitid = 145813;

COMMENT ON VIEW vw_enrollment_summary IS 'Pre-calculated enrollment metrics for dashboard consumption';

-- View for retention dashboard
CREATE OR REPLACE VIEW vw_retention_dashboard AS
SELECT
    r.year,
    r.full_time_retention,
    r.part_time_retention,
    r.pell_retention,
    r.non_pell_retention,
    r.first_gen_retention,
    r.not_first_gen_retention,
    ROUND(r.non_pell_retention - r.pell_retention, 2) AS pell_equity_gap,
    ROUND(r.not_first_gen_retention - r.first_gen_retention, 2) AS first_gen_gap,
    -- Benchmark comparison
    74.1 AS niu_retention_benchmark,
    82.4 AS illinois_state_benchmark,
    ROUND(r.full_time_retention - 74.1, 2) AS vs_niu,
    ROUND(r.full_time_retention - 82.4, 2) AS vs_illinois_state
FROM fact_retention_rates r
WHERE r.unitid = 145813;

COMMENT ON VIEW vw_retention_dashboard IS 'Retention metrics with equity gaps and peer benchmarks';
