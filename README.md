# UIS Student Success Analytics

**University of Illinois Springfield — Enrollment, Retention & Graduation Analytics**  
*Built for the Office of Institutional Research and Effectiveness (OIRE)*

[![Data Source: IPEDS](https://img.shields.io/badge/Data-IPEDS%20(NCES)-blue)](https://nces.ed.gov/ipeds/)
[![UIS Unit ID](https://img.shields.io/badge/UIS%20Unit%20ID-145813-orange)](https://nces.ed.gov/ipeds/datacenter/InstitutionProfile.aspx?unitId=145813)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Tests: 19/19](https://img.shields.io/badge/Tests-19%2F19%20Passing-brightgreen)](tests/test_data_quality.py)
[![Data Quality: 29/29](https://img.shields.io/badge/Data%20Quality-29%2F29%20Checks-brightgreen)](python/analysis/data_quality_report.py)

---

## 🔴 Live Interactive Dashboard

> **[▶ Open Live Dashboard](https://budige.github.io/uis-student-success-analytics/)**
>
> Deployed on GitHub Pages — fully interactive in any browser, no install needed.
> 6 tabs: Overview · Enrollment · Retention & Equity · Graduation · IL Benchmarks · Forecast

---

## Dashboard Screenshots

### Tab 1 — Overview: KPIs + Enrollment Trend + Retention by Group
![Overview Dashboard](docs/screenshots/screenshot_01_overview.png)

### Tab 2 — Graduation Rates & Illinois Peer Benchmarking
![Graduation & Benchmarks](docs/screenshots/screenshot_02_graduation_benchmarks.png)

### Tab 3 — Equity Analysis & Enrollment Forecast 2024–2026
![Equity & Forecast](docs/screenshots/screenshot_03_equity_forecast.png)

---

## What This Project Does

This project replicates the **exact type of analysis performed by UIS OIRE** — tracking student success outcomes using publicly available IPEDS (Integrated Postsecondary Education Data System) data.

It answers four questions OIRE reports on annually:

1. **Enrollment** — How is UIS enrollment trending? Who is enrolling and how has the mix changed?
2. **Retention** — Which student populations are at greatest risk of not returning year-to-year?
3. **Graduation** — Is the 6-year graduation rate improving? What is the trajectory toward HLC targets?
4. **Benchmarking** — How does UIS compare to Northern Illinois, Eastern Illinois, and other IL peers?

---

## Data Sources

All data is **real, public, and downloadable** from official government sources.

| Dataset | Source | Years | Rows |
|---------|--------|-------|------|
| UIS Fall Enrollment | [IPEDS Fall Enrollment Survey](https://nces.ed.gov/ipeds/datacenter/) | 2014–2023 | 10 |
| UIS Graduation Rates | [IPEDS Graduation Rate Survey (150%)](https://nces.ed.gov/ipeds/datacenter/) | 2010–2017 cohorts | 8 |
| UIS Retention Rates | [IPEDS Fall Enrollment - Retention](https://nces.ed.gov/ipeds/datacenter/) | 2014–2023 | 10 |
| UIS Financial Aid | [IPEDS Student Financial Aid Survey](https://nces.ed.gov/ipeds/datacenter/) | 2014–2023 | 10 |
| IL University Benchmarks | [IPEDS Data Center + College Scorecard](https://collegescorecard.ed.gov/) | 2023 | 9 institutions |

**UIS IPEDS Profile**: https://nces.ed.gov/ipeds/datacenter/InstitutionProfile.aspx?unitId=145813  
**Unit ID**: 145813 | **Sector**: Public, 4-year or above | **Carnegie**: Master's: Larger Programs

---

## Key Findings

| Metric | 2014 | 2023 | Change |
|--------|------|------|--------|
| Total Enrollment | 5,116 | 4,402 | −714 (−14.0%) |
| Online Enrollment % | 38.0% | 56.1% | +18.1pp — **#1 in Illinois** |
| Full-Time Retention | 67.3% | 71.9% | +4.6pp |
| 6-Year Grad Rate | 40.0% (2010 cohort) | 43.6% (2017 cohort) | +3.6pp |
| Pell Retention Gap | 10.2pp | 10.3pp | Persistent equity challenge |

**Critical OIRE Finding**: Pell grant students retain at 65.8% vs. non-Pell at 76.1% — a 10.3pp equity gap. Closing half this gap would retain ~35 additional students per year.

---

## Project Structure

```
uis-student-success-analytics/
│
├── docs/                           ← GitHub Pages (live dashboard)
│   ├── index.html                  ← Interactive dashboard (GitHub Pages)
│   └── screenshots/                ← Dashboard screenshots for README
│
├── data/
│   ├── raw/                        ← IPEDS source data (CSV)
│   │   ├── uis_enrollment_2014_2023.csv
│   │   ├── uis_graduation_rates_2010_2017.csv
│   │   ├── uis_retention_rates_2014_2023.csv
│   │   ├── uis_financial_aid_2014_2023.csv
│   │   ├── illinois_universities_comparison_2023.csv
│   │   └── DATA_SOURCES.md         ← Data provenance documentation
│   └── processed/                  ← Forecast outputs
│
├── sql/
│   ├── schema/
│   │   ├── 01_create_database.sql  ← PostgreSQL schema (star schema)
│   │   └── 02_load_data.sql        ← Data load script
│   ├── queries/
│   │   ├── 01_enrollment_trends.sql        ← YoY, moving avg, trend flags
│   │   ├── 02_retention_analysis.sql       ← Equity gaps, benchmarks
│   │   ├── 03_graduation_rate_analysis.sql ← Cohort outcomes, projections
│   │   ├── 04_peer_benchmarking.sql        ← IL university comparison
│   │   ├── 05_financial_aid_equity.sql     ← Pell trends, at-risk count
│   │   ├── 06_enrollment_forecast.sql      ← Linear regression, 3 scenarios
│   │   ├── 07_student_risk_scoring.sql     ← Composite risk score
│   │   └── 08_executive_dashboard_kpis.sql ← Single-query KPI feed
│   └── views/
│       └── 01_enrollment_summary_view.sql  ← Pre-built views for Power BI
│
├── python/
│   ├── etl/data_loader.py          ← ETL pipeline with validation + retry logic
│   ├── analysis/
│   │   ├── enrollment_analysis.py  ← 4 publication-quality charts
│   │   └── data_quality_report.py  ← 29-check data quality validator
│   └── models/enrollment_forecast.py ← Holt's model, MAPE 2.2%
│
├── notebooks/
│   └── 01_exploratory_analysis.ipynb
│
├── reports/
│   ├── charts/                     ← 5 PNG charts (150 DPI)
│   ├── key_metrics_summary.csv
│   └── oire_findings_summary.md    ← Executive summary for OIRE
│
├── docs/power_bi_connection_guide.md ← Step-by-step Power BI setup
├── tests/test_data_quality.py      ← 19 pytest tests, all passing
└── requirements.txt
```

---

## SQL Highlights — 8 Advanced Queries

```sql
-- Query 2: Retention equity gaps with peer benchmark comparison
WITH retention_trends AS (
    SELECT year,
        full_time_retention, pell_retention,
        ROUND(non_pell_retention - pell_retention, 2)   AS pell_equity_gap,
        LAG(full_time_retention) OVER (ORDER BY year)   AS prev_retention,
        AVG(full_time_retention) OVER (
            ORDER BY year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ft_retention_3yr_avg
    FROM fact_retention_rates WHERE unitid = 145813
)
SELECT year, pell_equity_gap,
    CASE WHEN pell_equity_gap > 12 THEN 'CRITICAL'
         WHEN pell_equity_gap > 8  THEN 'HIGH'
         ELSE 'MODERATE' END AS equity_gap_severity,
    ROUND(full_time_retention - 74.1, 2) AS vs_niu_benchmark
FROM retention_trends;
```

**SQL Techniques Used:**
`LAG()` · `RANK()` · `PERCENT_RANK()` · `FIRST_VALUE()` · `LAST_VALUE()` · rolling averages with `ROWS BETWEEN` · multi-step CTEs · `UNION ALL` scenario tables · correlated subqueries

---

## Running the Project

```bash
pip install -r requirements.txt

# Validate all data (29 checks)
python3 python/analysis/data_quality_report.py

# Generate charts
python3 python/analysis/enrollment_analysis.py

# Run forecasting model
python3 python/models/enrollment_forecast.py

# Run test suite
pytest tests/ -v

# Load PostgreSQL database
psql -U postgres -d uis_analytics -f sql/schema/01_create_database.sql
psql -U postgres -d uis_analytics -f sql/schema/02_load_data.sql
```

---

## Relevance to UIS OIRE

| OIRE Function | This Project |
|---------------|-------------|
| IBHE enrollment reporting | `sql/queries/01_enrollment_trends.sql` |
| HLC accreditation metrics | `sql/queries/03_graduation_rate_analysis.sql` |
| Student success dashboards | `docs/index.html` (live on GitHub Pages) |
| Peer institution comparison | `sql/queries/04_peer_benchmarking.sql` |
| Equity and access analysis | `sql/queries/05_financial_aid_equity.sql` |
| Strategic enrollment planning | `python/models/enrollment_forecast.py` |
| Data quality governance | `python/analysis/data_quality_report.py` |
| Annual report KPIs | `sql/queries/08_executive_dashboard_kpis.sql` |

---

## What I Learned

1. **IPEDS data structure** — the difference between Fall Enrollment Survey, Graduation Rate Survey, and Outcome Measures matters for how you interpret "graduation rate"
2. **Retention vs. graduation** — these measure completely different things. A high transfer rate at UIS doesn't mean failure; many students transfer to UIUC
3. **Equity gap measurement** — the raw percentage gap understates the problem; I added "estimated students at risk" to make it actionable
4. **Online enrollment reporting** — UIS's 56% online rate puts it in a different peer group than traditional residential institutions

> **TODO**: Add direct IPEDS API integration when NCES publishes their REST API (currently in beta)  
> **TODO**: Extend with 2-year retention rates once IPEDS provides them  
> **TODO**: Connect to Banner SIS for real-time early alert integration  

---

## Author

**Rakesh Budige** | MS Computer Science, University of Illinois Springfield (April 2026)  
GitHub: [github.com/Budige](https://github.com/Budige)

*Data Source: IPEDS Data Center, National Center for Education Statistics — nces.ed.gov/ipeds | UIS Unit ID: 145813*
