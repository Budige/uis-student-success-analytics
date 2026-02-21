-- ============================================================
-- Query 6: Enrollment Forecasting - Linear Trend Analysis
-- Purpose: Project 3-year enrollment for strategic planning
-- Relevant to: OIRE Budget Planning, Capacity Planning
-- Author: Rakesh Budige
-- Last modified: 2025-02-10 (added scenario columns)
-- ============================================================

-- NOTE: This SQL provides trend coefficients fed into Python ARIMA model
-- Full forecast visualization is in python/analysis/enrollment_forecast.py

WITH enrollment_indexed AS (
    SELECT
        year,
        total_enrollment,
        undergrad_enrollment,
        grad_enrollment,
        online_only,
        -- Index for regression (year 2014 = 1)
        year - 2013 AS t,
        -- Normalized enrollment (base = 2014 = 100)
        ROUND(total_enrollment::DECIMAL / 5116 * 100, 2) AS enrollment_index
    FROM fact_enrollment
    WHERE unitid = 145813
),
regression_components AS (
    SELECT
        year, t, total_enrollment, enrollment_index,
        undergrad_enrollment, grad_enrollment, online_only,
        -- Linear regression: y = a + b*t
        AVG(total_enrollment) OVER () AS mean_enrollment,
        AVG(t) OVER () AS mean_t,
        SUM((t - AVG(t) OVER ()) * (total_enrollment - AVG(total_enrollment) OVER ())) OVER () AS cov_t_y,
        SUM((t - AVG(t) OVER ()) ^ 2) OVER () AS var_t
    FROM enrollment_indexed
),
linear_regression AS (
    SELECT
        year, t, total_enrollment, enrollment_index,
        undergrad_enrollment, grad_enrollment, online_only,
        -- Regression coefficients
        cov_t_y / NULLIF(var_t, 0) AS slope,
        mean_enrollment - (cov_t_y / NULLIF(var_t, 0)) * mean_t AS intercept,
        -- Fitted values
        mean_enrollment + (cov_t_y / NULLIF(var_t, 0)) * (t - mean_t) AS fitted_value,
        -- Residuals
        total_enrollment - (mean_enrollment + (cov_t_y / NULLIF(var_t, 0)) * (t - mean_t)) AS residual
    FROM regression_components
),
forecast_scenarios AS (
    SELECT
        year, total_enrollment, fitted_value,
        ROUND(residual) AS residual,
        ROUND(slope) AS annual_trend,
        -- 3-year forecast scenarios
        ROUND(fitted_value + slope * 1) AS forecast_2024_baseline,
        ROUND(fitted_value + slope * 2) AS forecast_2025_baseline,
        ROUND(fitted_value + slope * 3) AS forecast_2026_baseline,
        -- Optimistic: 1.5% annual growth (targeted recruitment)
        ROUND(total_enrollment * POWER(1.015, 1)) AS forecast_2024_optimistic,
        ROUND(total_enrollment * POWER(1.015, 2)) AS forecast_2025_optimistic,
        ROUND(total_enrollment * POWER(1.015, 3)) AS forecast_2026_optimistic,
        -- Conservative: continued decline at -1% per year
        ROUND(total_enrollment * POWER(0.99, 1)) AS forecast_2024_conservative,
        ROUND(total_enrollment * POWER(0.99, 2)) AS forecast_2025_conservative,
        ROUND(total_enrollment * POWER(0.99, 3)) AS forecast_2026_conservative,
        -- R-squared (model fit quality)
        1 - (SUM(residual^2) OVER () / NULLIF(
            SUM((total_enrollment - AVG(total_enrollment) OVER ())^2) OVER (), 0
        )) AS r_squared
    FROM linear_regression
    WHERE year = (SELECT MAX(year) FROM fact_enrollment WHERE unitid = 145813)
)
SELECT
    '2023 Actual' AS scenario,
    total_enrollment AS enrollment,
    NULL::INTEGER AS forecast_2024,
    NULL::INTEGER AS forecast_2025,
    NULL::INTEGER AS forecast_2026,
    ROUND(r_squared, 4) AS model_r_squared
FROM forecast_scenarios
UNION ALL
SELECT 'Baseline (Linear Trend)', total_enrollment,
    forecast_2024_baseline, forecast_2025_baseline, forecast_2026_baseline, ROUND(r_squared, 4)
FROM forecast_scenarios
UNION ALL
SELECT 'Optimistic (1.5%/yr Growth)', total_enrollment,
    forecast_2024_optimistic, forecast_2025_optimistic, forecast_2026_optimistic, ROUND(r_squared, 4)
FROM forecast_scenarios
UNION ALL
SELECT 'Conservative (1% Decline)', total_enrollment,
    forecast_2024_conservative, forecast_2025_conservative, forecast_2026_conservative, ROUND(r_squared, 4)
FROM forecast_scenarios;
