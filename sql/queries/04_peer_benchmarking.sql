-- ============================================================
-- Query 4: Peer Institution Benchmarking
-- Purpose: Position UIS among Illinois public universities
-- Relevant to: OIRE Peer Comparison, Strategic Planning
-- Author: Rakesh Budige
-- ============================================================

WITH il_rankings AS (
    SELECT
        b.unitid,
        i.institution_name,
        b.total_enrollment,
        b.grad_rate_6yr,
        b.retention_rate,
        b.pell_grant_pct,
        b.online_pct,
        b.full_time_pct,
        b.median_earnings_10yr,
        b.admit_rate,
        -- Rank each metric (1 = best)
        RANK() OVER (ORDER BY b.grad_rate_6yr DESC) AS grad_rate_rank,
        RANK() OVER (ORDER BY b.retention_rate DESC) AS retention_rank,
        RANK() OVER (ORDER BY b.median_earnings_10yr DESC) AS earnings_rank,
        RANK() OVER (ORDER BY b.pell_grant_pct DESC) AS pell_access_rank,
        -- Percentile for each metric
        PERCENT_RANK() OVER (ORDER BY b.grad_rate_6yr) AS grad_rate_pctile,
        PERCENT_RANK() OVER (ORDER BY b.retention_rate) AS retention_pctile,
        -- Averages across all IL institutions
        AVG(b.grad_rate_6yr) OVER () AS il_avg_grad_rate,
        AVG(b.retention_rate) OVER () AS il_avg_retention,
        AVG(b.median_earnings_10yr) OVER () AS il_avg_earnings,
        -- UIS-specific comparison flag
        CASE WHEN b.unitid = 145813 THEN TRUE ELSE FALSE END AS is_uis,
        -- Peer group flag (similar size: 3000-10000 enrollment)
        CASE 
            WHEN b.total_enrollment BETWEEN 3000 AND 10000 THEN TRUE 
            ELSE FALSE 
        END AS is_peer_institution
    FROM fact_il_benchmarks b
    JOIN dim_institution i ON b.unitid = i.unitid
    WHERE b.year = 2023
),
uis_vs_peers AS (
    SELECT
        *,
        -- Gap to IL average
        ROUND(grad_rate_6yr - il_avg_grad_rate, 2) AS gap_to_il_avg_grad,
        ROUND(retention_rate - il_avg_retention, 2) AS gap_to_il_avg_retention,
        -- UIS reference values for comparison
        MAX(CASE WHEN unitid = 145813 THEN grad_rate_6yr END) OVER () AS uis_grad_rate,
        MAX(CASE WHEN unitid = 145813 THEN retention_rate END) OVER () AS uis_retention
    FROM il_rankings
)
SELECT
    institution_name,
    total_enrollment,
    grad_rate_6yr AS "6yr Grad Rate",
    grad_rate_rank AS "Grad Rank (IL)",
    retention_rate AS "Retention Rate",
    retention_rank AS "Retention Rank (IL)",
    pell_grant_pct AS "Pell Grant %",
    pell_access_rank AS "Access Rank (IL)",
    online_pct AS "Online %",
    median_earnings_10yr AS "Median Earnings (10yr)",
    earnings_rank AS "Earnings Rank (IL)",
    ROUND(il_avg_grad_rate, 2) AS "IL Avg Grad Rate",
    ROUND(il_avg_retention, 2) AS "IL Avg Retention",
    gap_to_il_avg_grad AS "Gap to IL Avg (Grad)",
    gap_to_il_avg_retention AS "Gap to IL Avg (Retention)",
    CASE WHEN is_uis THEN '⭐ UIS' ELSE '' END AS "Focus",
    CASE WHEN is_peer_institution THEN 'Peer' ELSE 'Non-Peer' END AS "Peer Group"
FROM uis_vs_peers
ORDER BY grad_rate_6yr DESC;

-- ============================================================
-- Query 4b: UIS Strengths Analysis
-- Areas where UIS performs above peer average
-- ============================================================
WITH peer_avgs AS (
    SELECT
        AVG(CASE WHEN total_enrollment BETWEEN 3000 AND 10000 THEN grad_rate_6yr END) AS peer_avg_grad,
        AVG(CASE WHEN total_enrollment BETWEEN 3000 AND 10000 THEN retention_rate END) AS peer_avg_retention,
        AVG(CASE WHEN total_enrollment BETWEEN 3000 AND 10000 THEN pell_grant_pct END) AS peer_avg_pell,
        AVG(CASE WHEN total_enrollment BETWEEN 3000 AND 10000 THEN online_pct END) AS peer_avg_online,
        AVG(CASE WHEN total_enrollment BETWEEN 3000 AND 10000 THEN median_earnings_10yr END) AS peer_avg_earnings
    FROM fact_il_benchmarks
    WHERE year = 2023
),
uis_data AS (
    SELECT grad_rate_6yr, retention_rate, pell_grant_pct, online_pct, median_earnings_10yr
    FROM fact_il_benchmarks WHERE unitid = 145813 AND year = 2023
)
SELECT
    'Graduation Rate' AS metric,
    uis_data.grad_rate_6yr AS uis_value,
    ROUND(peer_avgs.peer_avg_grad, 2) AS peer_avg,
    ROUND(uis_data.grad_rate_6yr - peer_avgs.peer_avg_grad, 2) AS vs_peer_avg,
    CASE WHEN uis_data.grad_rate_6yr > peer_avgs.peer_avg_grad THEN '✓ Above Peers' ELSE '✗ Below Peers' END AS status
FROM uis_data, peer_avgs
UNION ALL
SELECT 'Retention Rate', retention_rate, ROUND(peer_avg_retention, 2),
    ROUND(retention_rate - peer_avg_retention, 2),
    CASE WHEN retention_rate > peer_avg_retention THEN '✓ Above Peers' ELSE '✗ Below Peers' END
FROM uis_data, peer_avgs
UNION ALL
SELECT 'Online Enrollment %', online_pct, ROUND(peer_avg_online, 2),
    ROUND(online_pct - peer_avg_online, 2),
    CASE WHEN online_pct > peer_avg_online THEN '✓ Above Peers' ELSE '✗ Below Peers' END
FROM uis_data, peer_avgs
UNION ALL
SELECT 'Pell Grant Access', pell_grant_pct, ROUND(peer_avg_pell, 2),
    ROUND(pell_grant_pct - peer_avg_pell, 2),
    CASE WHEN pell_grant_pct > peer_avg_pell THEN '✓ Above Peers (Accessible)' ELSE '✗ Below Peers' END
FROM uis_data, peer_avgs;
