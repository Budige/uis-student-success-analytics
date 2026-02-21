-- ============================================================
-- Query 8: Executive Dashboard KPIs
-- Purpose: Single query for OIRE annual report KPIs
-- Relevant to: OIRE Annual Report, President's Dashboard
-- Author: Rakesh Budige
-- ============================================================

-- This query feeds the Power BI executive dashboard
-- Joins enrollment + retention + graduation + financial aid for single view

WITH latest_year_data AS (
    SELECT
        e.year,
        e.total_enrollment,
        e.undergrad_enrollment,
        e.grad_enrollment,
        e.full_time,
        e.part_time,
        e.online_only,
        e.female,
        e.black,
        e.hispanic,
        r.full_time_retention,
        r.pell_retention,
        r.first_gen_retention,
        fa.pell_recipients,
        fa.pell_pct_undergrad,
        fa.avg_net_price_0_30k,
        fa.any_aid_pct,
        -- YoY enrollment change
        LAG(e.total_enrollment) OVER (ORDER BY e.year) AS prev_enrollment,
        LAG(r.full_time_retention) OVER (ORDER BY e.year) AS prev_retention
    FROM fact_enrollment e
    JOIN fact_retention_rates r ON e.unitid = r.unitid AND e.year = r.year
    JOIN fact_financial_aid fa ON e.unitid = fa.unitid AND e.year = fa.year
    WHERE e.unitid = 145813
),
kpi_calculations AS (
    SELECT
        year,
        total_enrollment,
        undergrad_enrollment,
        grad_enrollment,
        full_time,
        part_time,
        online_only,
        female,
        black,
        hispanic,
        full_time_retention,
        pell_retention,
        first_gen_retention,
        pell_recipients,
        pell_pct_undergrad,
        avg_net_price_0_30k,
        any_aid_pct,
        -- Enrollment change KPIs
        total_enrollment - prev_enrollment AS enrollment_yoy_change,
        ROUND((total_enrollment - prev_enrollment)::DECIMAL / NULLIF(prev_enrollment,0) * 100, 2)
            AS enrollment_yoy_pct,
        full_time_retention - prev_retention AS retention_yoy_change,
        -- Diversity KPIs
        ROUND((black + hispanic)::DECIMAL / total_enrollment * 100, 1) AS black_hispanic_pct,
        ROUND(female::DECIMAL / total_enrollment * 100, 1) AS female_pct,
        ROUND(online_only::DECIMAL / total_enrollment * 100, 1) AS online_pct,
        ROUND(full_time::DECIMAL / total_enrollment * 100, 1) AS full_time_pct
    FROM latest_year_data
)
SELECT
    year AS "Academic Year",
    total_enrollment AS "Total Enrollment",
    enrollment_yoy_change AS "Enrollment Change (YoY)",
    enrollment_yoy_pct AS "Enrollment Change %",
    undergrad_enrollment AS "Undergraduate",
    grad_enrollment AS "Graduate",
    full_time_pct AS "Full-Time %",
    online_pct AS "Online %",
    full_time_retention AS "Retention Rate (FT)",
    pell_retention AS "Pell Retention Rate",
    first_gen_retention AS "First-Gen Retention",
    retention_yoy_change AS "Retention Change (YoY)",
    pell_recipients AS "Pell Recipients",
    pell_pct_undergrad AS "Pell % of UG",
    avg_net_price_0_30k AS "Net Price (0-30k Income)",
    any_aid_pct AS "% Receiving Any Aid",
    female_pct AS "Female %",
    black_hispanic_pct AS "Black+Hispanic %",
    -- Status indicators
    CASE WHEN enrollment_yoy_pct >= 0 THEN '↑ Growing' ELSE '↓ Declining' END AS "Enrollment Status",
    CASE WHEN full_time_retention >= 71 THEN '✓ On Track' ELSE '⚠ Monitor' END AS "Retention Status"
FROM kpi_calculations
ORDER BY year DESC
LIMIT 5;  -- Last 5 years for dashboard
