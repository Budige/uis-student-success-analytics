-- ============================================================
-- Query 5: Financial Aid & Equity Analysis
-- Purpose: Analyze Pell recipient trends and net price impact
-- Relevant to: OIRE Access & Equity Reporting, IBHE
-- Author: Rakesh Budige
-- ============================================================

WITH aid_trends AS (
    SELECT
        fa.year,
        fa.pell_recipients,
        fa.pell_pct_undergrad,
        fa.subsidized_loan_recipients,
        fa.avg_net_price_0_30k,
        fa.avg_net_price_30_48k,
        fa.avg_net_price_48_75k,
        fa.avg_net_price_75_110k,
        fa.any_aid_pct,
        e.undergrad_enrollment,
        -- Pell affordability: net price as % of typical income for lowest bracket
        ROUND(fa.avg_net_price_0_30k / 15000.0 * 100, 1) AS net_price_pct_of_low_income,
        -- Year-over-year change in Pell recipients
        LAG(fa.pell_recipients) OVER (ORDER BY fa.year) AS prev_pell,
        LAG(fa.avg_net_price_0_30k) OVER (ORDER BY fa.year) AS prev_net_price_low,
        -- Net price increase rate
        LAG(fa.avg_net_price_0_30k, 5) OVER (ORDER BY fa.year) AS net_price_5yr_ago
    FROM fact_financial_aid fa
    JOIN fact_enrollment e ON fa.unitid = e.unitid AND fa.year = e.year
    WHERE fa.unitid = 145813
)
SELECT
    year,
    pell_recipients,
    pell_pct_undergrad AS pell_pct,
    subsidized_loan_recipients,
    any_aid_pct,
    avg_net_price_0_30k AS net_price_lowest_bracket,
    avg_net_price_30_48k AS net_price_low_bracket,
    avg_net_price_48_75k AS net_price_mid_bracket,
    avg_net_price_75_110k AS net_price_upper_bracket,
    net_price_pct_of_low_income,
    -- YoY Pell change
    pell_recipients - prev_pell AS pell_yoy_change,
    ROUND((pell_recipients - prev_pell)::DECIMAL / NULLIF(prev_pell, 0) * 100, 2) AS pell_yoy_pct,
    -- 5-year net price increase for lowest income bracket
    avg_net_price_0_30k - net_price_5yr_ago AS net_price_5yr_increase,
    -- Affordability tier
    CASE
        WHEN net_price_pct_of_low_income < 75 THEN 'AFFORDABLE'
        WHEN net_price_pct_of_low_income < 90 THEN 'CHALLENGING'
        ELSE 'UNAFFORDABLE'
    END AS affordability_status,
    -- Net price spread (equity indicator)
    ROUND(avg_net_price_75_110k - avg_net_price_0_30k, 0) AS net_price_spread
FROM aid_trends
ORDER BY year;

-- ============================================================
-- Query 5b: Retention-Aid Correlation
-- Key insight: Pell students have lower retention - quantify gap
-- ============================================================
SELECT
    r.year,
    fa.pell_pct_undergrad,
    r.pell_retention,
    r.non_pell_retention,
    ROUND(r.non_pell_retention - r.pell_retention, 2) AS retention_equity_gap,
    fa.avg_net_price_0_30k,
    -- Estimate students at risk (Pell students with below-average retention)
    ROUND(e.undergrad_enrollment * fa.pell_pct_undergrad / 100 * 
          (r.non_pell_retention - r.pell_retention) / 100) AS estimated_at_risk_students,
    -- If we closed the gap halfway, how many more would retain?
    ROUND(e.undergrad_enrollment * fa.pell_pct_undergrad / 100 * 
          (r.non_pell_retention - r.pell_retention) / 100 * 0.5) AS half_gap_students_retained
FROM fact_retention_rates r
JOIN fact_financial_aid fa ON r.unitid = fa.unitid AND r.year = fa.year
JOIN fact_enrollment e ON r.unitid = e.unitid AND r.year = e.year
WHERE r.unitid = 145813
ORDER BY r.year;
