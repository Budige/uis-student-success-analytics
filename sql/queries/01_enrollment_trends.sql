-- ============================================================
-- Query 1: Enrollment Trends Analysis with Year-over-Year Change
-- Purpose: Track UIS enrollment decline and stabilization
-- Relevant to: OIRE Strategic Planning, IBHE Reporting
-- Author: Rakesh Budige
-- ============================================================

WITH enrollment_with_lag AS (
    SELECT
        e.year,
        e.total_enrollment,
        e.undergrad_enrollment,
        e.grad_enrollment,
        e.full_time,
        e.part_time,
        e.online_only,
        -- Year-over-year changes
        LAG(e.total_enrollment, 1) OVER (ORDER BY e.year) AS prev_total,
        LAG(e.undergrad_enrollment, 1) OVER (ORDER BY e.year) AS prev_undergrad,
        -- 3-year moving average to smooth COVID noise
        AVG(e.total_enrollment) OVER (
            ORDER BY e.year
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS moving_avg_3yr,
        -- Cumulative change from 2014 baseline
        FIRST_VALUE(e.total_enrollment) OVER (ORDER BY e.year) AS baseline_2014
    FROM fact_enrollment e
    WHERE e.unitid = 145813
),
enrollment_metrics AS (
    SELECT
        year,
        total_enrollment,
        undergrad_enrollment,
        grad_enrollment,
        full_time,
        part_time,
        online_only,
        prev_total,
        ROUND(moving_avg_3yr) AS moving_avg_3yr,
        -- YoY change
        total_enrollment - prev_total AS yoy_change,
        ROUND(
            (total_enrollment - prev_total)::DECIMAL / NULLIF(prev_total, 0) * 100, 2
        ) AS yoy_pct_change,
        -- Cumulative change from 2014
        total_enrollment - baseline_2014 AS cumulative_change,
        ROUND(
            (total_enrollment - baseline_2014)::DECIMAL / baseline_2014 * 100, 2
        ) AS cumulative_pct_change,
        -- Enrollment mix
        ROUND(full_time::DECIMAL / total_enrollment * 100, 1) AS full_time_pct,
        ROUND(online_only::DECIMAL / total_enrollment * 100, 1) AS online_pct,
        ROUND(grad_enrollment::DECIMAL / total_enrollment * 100, 1) AS grad_pct
    FROM enrollment_with_lag
)
SELECT
    year,
    total_enrollment,
    undergrad_enrollment,
    grad_enrollment,
    yoy_change,
    yoy_pct_change,
    cumulative_change,
    cumulative_pct_change,
    moving_avg_3yr,
    full_time_pct,
    online_pct,
    grad_pct,
    -- Flag enrollment trend direction
    CASE
        WHEN yoy_pct_change >= 1.0 THEN 'GROWTH'
        WHEN yoy_pct_change >= -0.5 THEN 'STABLE'
        WHEN yoy_pct_change >= -2.0 THEN 'DECLINE'
        ELSE 'SIGNIFICANT DECLINE'
    END AS enrollment_trend
FROM enrollment_metrics
ORDER BY year;

-- ============================================================
-- Query 1b: Demographic Diversity Trends
-- ============================================================
SELECT
    year,
    total_enrollment,
    white,
    black,
    hispanic,
    asian,
    -- Diversity metrics
    ROUND((black + hispanic + asian + two_or_more)::DECIMAL / total_enrollment * 100, 1)
        AS urm_pct,
    ROUND(black::DECIMAL / total_enrollment * 100, 1) AS black_pct,
    ROUND(hispanic::DECIMAL / total_enrollment * 100, 1) AS hispanic_pct,
    ROUND(nonresident_alien::DECIMAL / total_enrollment * 100, 1) AS intl_pct,
    -- Gender
    ROUND(female::DECIMAL / total_enrollment * 100, 1) AS female_pct
FROM fact_enrollment
WHERE unitid = 145813
ORDER BY year;
