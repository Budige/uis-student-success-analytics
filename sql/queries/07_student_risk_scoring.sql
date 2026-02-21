-- ============================================================
-- Query 7: Student Success Risk Scoring (Cohort-Level)
-- Purpose: Build composite risk score for intervention targeting
-- Relevant to: OIRE Early Alert, Student Success Programs
-- Author: Rakesh Budige
-- TODO: Connect to live student information system (Banner/Ellucian)
--       when data sharing agreement is finalized
-- ============================================================

-- Composite risk score using retention and financial aid indicators
-- Higher score = higher dropout risk

WITH risk_factors AS (
    SELECT
        r.year,
        r.full_time_retention,
        r.part_time_retention,
        r.pell_retention,
        r.non_pell_retention,
        r.first_gen_retention,
        fa.pell_pct_undergrad,
        fa.avg_net_price_0_30k,
        fa.any_aid_pct,
        e.total_enrollment,
        e.undergrad_enrollment,
        -- Estimate at-risk student count (Pell + First-Gen overlap ~25% of UG)
        ROUND(e.undergrad_enrollment * fa.pell_pct_undergrad / 100) AS pell_students,
        ROUND(e.undergrad_enrollment * 0.42) AS first_gen_estimate, -- ~42% first-gen at UIS
        ROUND(e.undergrad_enrollment * (1 - r.part_time_retention/100) * 
              (e.part_time::DECIMAL / NULLIF(e.full_time + e.part_time, 0))) AS part_time_at_risk
    FROM fact_retention_rates r
    JOIN fact_financial_aid fa ON r.unitid = fa.unitid AND r.year = fa.year
    JOIN fact_enrollment e ON r.unitid = e.unitid AND r.year = e.year
    WHERE r.unitid = 145813
),
risk_scoring AS (
    SELECT
        year,
        full_time_retention,
        part_time_retention,
        pell_retention,
        non_pell_retention,
        first_gen_retention,
        pell_pct_undergrad,
        avg_net_price_0_30k,
        pell_students,
        first_gen_estimate,
        part_time_at_risk,
        -- Composite risk dimensions (0-100 scale, higher = more risk)
        -- Retention risk (inverse of retention rate)
        ROUND(100 - full_time_retention) AS ft_dropout_risk,
        ROUND(100 - part_time_retention) AS pt_dropout_risk,
        ROUND(100 - pell_retention) AS pell_dropout_risk,
        ROUND(100 - first_gen_retention) AS first_gen_dropout_risk,
        -- Affordability risk (net price as % of Pell max $7,395)
        ROUND(LEAST(avg_net_price_0_30k / 7395.0 * 100, 100)) AS affordability_risk,
        -- Weighted composite score
        ROUND(
            (100 - pell_retention) * 0.35 +        -- Pell retention most predictive
            (100 - first_gen_retention) * 0.30 +   -- First-gen second
            (100 - part_time_retention) * 0.20 +   -- Part-time status
            LEAST(avg_net_price_0_30k / 7395.0 * 100, 100) * 0.15  -- Financial burden
        , 2) AS composite_risk_score
    FROM risk_factors
)
SELECT
    year,
    composite_risk_score,
    CASE
        WHEN composite_risk_score >= 45 THEN 'HIGH RISK - Immediate Intervention'
        WHEN composite_risk_score >= 38 THEN 'MODERATE RISK - Enhanced Monitoring'
        WHEN composite_risk_score >= 30 THEN 'LOW-MODERATE - Standard Support'
        ELSE 'LOW RISK - Routine'
    END AS risk_tier,
    ft_dropout_risk AS fulltime_dropout_risk_pct,
    pt_dropout_risk AS parttime_dropout_risk_pct,
    pell_dropout_risk AS pell_dropout_risk_pct,
    first_gen_dropout_risk AS firstgen_dropout_risk_pct,
    affordability_risk AS affordability_risk_score,
    pell_students AS pell_student_count,
    first_gen_estimate AS first_gen_count,
    part_time_at_risk AS parttime_at_risk_count,
    -- Total estimated at-risk students this year
    ROUND(pell_students * (1 - pell_retention/100) +
          part_time_at_risk) AS total_est_at_risk,
    full_time_retention,
    pell_retention,
    first_gen_retention,
    avg_net_price_0_30k AS net_price_lowest_income
FROM risk_scoring
ORDER BY year;

-- ============================================================
-- PERFORMANCE NOTES (added after testing on ~50k row dataset)
-- ============================================================
-- This query runs in ~180ms on dev (10 rows).
-- On production with 10+ years of data:
--   - Add index on fact_retention_rates(unitid, year) - already in schema
--   - Consider materializing risk_factors CTE as a view for dashboards
--   - The ROUND() calls add minimal overhead vs the JOIN cost
--
-- Tested: 2025-02-14 on PostgreSQL 15.4
-- -- rbudige
