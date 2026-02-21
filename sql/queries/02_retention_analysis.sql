-- ============================================================
-- Query 2: Retention Rate Analysis & Equity Gaps
-- Purpose: Identify at-risk student populations for interventions
-- Relevant to: OIRE Student Success Reporting, HLC Accreditation
-- Author: Rakesh Budige
-- ============================================================

-- Retention trend with rolling averages
WITH retention_trends AS (
    SELECT
        r.year,
        r.full_time_retention,
        r.part_time_retention,
        r.pell_retention,
        r.non_pell_retention,
        r.first_gen_retention,
        r.not_first_gen_retention,
        -- Equity gaps (difference between higher and lower performing groups)
        ROUND(r.non_pell_retention - r.pell_retention, 2) AS pell_equity_gap,
        ROUND(r.not_first_gen_retention - r.first_gen_retention, 2) AS first_gen_gap,
        ROUND(r.full_time_retention - r.part_time_retention, 2) AS attendance_gap,
        -- Overall retention benchmark: enrollment-weighted avg
        ROUND(
            (r.full_time_retention * e.full_time + r.part_time_retention * e.part_time)
            / NULLIF(e.full_time + e.part_time, 0), 2
        ) AS weighted_avg_retention,
        -- Year-over-year improvement
        LAG(r.full_time_retention) OVER (ORDER BY r.year) AS prev_ft_retention,
        LAG(r.pell_retention) OVER (ORDER BY r.year) AS prev_pell_retention
    FROM fact_retention_rates r
    JOIN fact_enrollment e ON r.unitid = e.unitid AND r.year = e.year
    WHERE r.unitid = 145813
),
retention_with_improvement AS (
    SELECT
        *,
        ROUND(full_time_retention - prev_ft_retention, 2) AS ft_yoy_improvement,
        ROUND(pell_retention - prev_pell_retention, 2) AS pell_yoy_improvement,
        -- Rolling 3-year avg for trend detection
        AVG(full_time_retention) OVER (
            ORDER BY year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ft_retention_3yr_avg,
        AVG(pell_equity_gap) OVER (
            ORDER BY year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS avg_equity_gap_3yr
    FROM retention_trends
)
SELECT
    year,
    full_time_retention,
    part_time_retention,
    pell_retention,
    non_pell_retention,
    first_gen_retention,
    not_first_gen_retention,
    pell_equity_gap,
    first_gen_gap,
    attendance_gap,
    weighted_avg_retention,
    ft_yoy_improvement,
    pell_yoy_improvement,
    ROUND(ft_retention_3yr_avg, 2) AS ft_retention_3yr_avg,
    ROUND(avg_equity_gap_3yr, 2) AS avg_equity_gap_3yr,
    -- Classify equity gap severity
    CASE
        WHEN pell_equity_gap > 12 THEN 'CRITICAL'
        WHEN pell_equity_gap > 8  THEN 'HIGH'
        WHEN pell_equity_gap > 5  THEN 'MODERATE'
        ELSE 'LOW'
    END AS equity_gap_severity,
    -- Compare to IL benchmark (NIU: 74.1 full-time retention)
    ROUND(full_time_retention - 74.1, 2) AS vs_niu_benchmark,
    ROUND(full_time_retention - 82.4, 2) AS vs_illinois_state_benchmark
FROM retention_with_improvement
ORDER BY year;
