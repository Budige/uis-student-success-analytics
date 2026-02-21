-- ============================================================
-- Query 3: Graduation Rate Cohort Analysis
-- Purpose: 6-year graduation rate trends, outcome tracking
-- Relevant to: OIRE HLC Reporting, IBHE Accountability
-- Author: Rakesh Budige
-- ============================================================

WITH graduation_cohorts AS (
    SELECT
        g.cohort_year,
        g.cohort_size,
        g.grad_6yr_total,
        g.grad_6yr_rate,
        g.grad_4yr_rate,
        g.transferred_out,
        g.still_enrolled,
        g.withdrew,
        -- Outcome percentages
        ROUND(g.transferred_out::DECIMAL / g.cohort_size * 100, 2) AS transfer_rate,
        ROUND(g.still_enrolled::DECIMAL / g.cohort_size * 100, 2) AS still_enrolled_rate,
        ROUND(g.withdrew::DECIMAL / g.cohort_size * 100, 2) AS withdrawal_rate,
        -- Completion rate (grad + transfer)
        ROUND((g.grad_6yr_total + g.transferred_out)::DECIMAL / g.cohort_size * 100, 2)
            AS completion_rate,
        -- Trend: improvement vs prior cohort
        LAG(g.grad_6yr_rate) OVER (ORDER BY g.cohort_year) AS prev_6yr_rate,
        LAG(g.grad_4yr_rate) OVER (ORDER BY g.cohort_year) AS prev_4yr_rate,
        -- Percentile rank of this cohort's 6yr rate
        PERCENT_RANK() OVER (ORDER BY g.grad_6yr_rate) AS grad_rate_percentile,
        -- Running average to detect trend
        AVG(g.grad_6yr_rate) OVER (
            ORDER BY g.cohort_year ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS trailing_4yr_avg
    FROM fact_graduation_rates g
    WHERE g.unitid = 145813
),
cohort_improvements AS (
    SELECT
        *,
        ROUND(grad_6yr_rate - prev_6yr_rate, 2) AS yoy_grad_improvement,
        ROUND(grad_4yr_rate - prev_4yr_rate, 2) AS yoy_4yr_improvement,
        -- Project future rate based on trend
        grad_6yr_rate + ROUND(AVG(grad_6yr_rate - prev_6yr_rate) OVER (
            ORDER BY cohort_year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2) AS projected_next_rate
    FROM graduation_cohorts
)
SELECT
    cohort_year AS "Cohort Year",
    cohort_size AS "Cohort Size",
    grad_6yr_rate AS "6-Year Grad Rate (%)",
    grad_4yr_rate AS "4-Year Grad Rate (%)",
    completion_rate AS "Completion Rate (Grad+Transfer)",
    transfer_rate AS "Transfer Rate (%)",
    withdrawal_rate AS "Withdrawal Rate (%)",
    yoy_grad_improvement AS "YoY Improvement",
    ROUND(trailing_4yr_avg, 2) AS "4-Year Trailing Avg",
    ROUND(projected_next_rate, 2) AS "Projected Next Cohort",
    -- Benchmark comparison (IL public avg ~52%)
    ROUND(grad_6yr_rate - 52.0, 2) AS "vs. IL Public Avg",
    -- HLC threshold flag
    CASE
        WHEN grad_6yr_rate >= 50 THEN '✓ Above 50% Threshold'
        WHEN grad_6yr_rate >= 40 THEN '⚠ Approaching Threshold'
        ELSE '✗ Below Threshold'
    END AS "HLC Status"
FROM cohort_improvements
ORDER BY cohort_year;
