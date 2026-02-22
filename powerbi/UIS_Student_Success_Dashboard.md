# Power BI Dashboard — Build Instructions

## How to Recreate This Dashboard in Power BI Desktop

This document provides the **exact steps** to build the UIS Student Success Dashboard
in Power BI Desktop using the CSV data files in `data/raw/`.

---

## Step 1 — Import Data

Open Power BI Desktop → **Get Data** → **Text/CSV**, import all 5 files:

| File | Table Name |
|------|-----------|
| `data/raw/uis_enrollment_2014_2023.csv` | `Enrollment` |
| `data/raw/uis_retention_rates_2014_2023.csv` | `Retention` |
| `data/raw/uis_graduation_rates_2010_2017.csv` | `Graduation` |
| `data/raw/uis_financial_aid_2014_2023.csv` | `FinancialAid` |
| `data/raw/illinois_universities_comparison_2023.csv` | `ILBenchmarks` |

---

## Step 2 — Data Model (Relationships)

In **Model View**, create these relationships:

```
Enrollment[year] → Retention[year]       (Many:1)
Enrollment[year] → FinancialAid[year]    (Many:1)
```

---

## Step 3 — DAX Measures

Create a `Measures` table, then add these DAX measures:

```dax
-- Enrollment YoY Change
Enrollment YoY Change = 
    VAR CurrentYear = MAX(Enrollment[total_enrollment])
    VAR PreviousYear = CALCULATE(
        MAX(Enrollment[total_enrollment]),
        DATEADD(Enrollment[year], -1, YEAR)
    )
    RETURN CurrentYear - PreviousYear

-- Pell Equity Gap
Pell Equity Gap = 
    MAX(Retention[non_pell_retention]) - MAX(Retention[pell_retention])

-- Online Enrollment %
Online % = 
    DIVIDE(MAX(Enrollment[online_only]), MAX(Enrollment[total_enrollment])) * 100

-- Grad Rate Improvement (latest vs earliest cohort)
Grad Rate Improvement = 
    MAXX(Graduation, Graduation[grad_6yr_rate]) - 
    MINX(Graduation, Graduation[grad_6yr_rate])

-- UIS vs NIU Retention Benchmark
vs NIU Benchmark = 
    MAX(Retention[full_time_retention]) - 74.1

-- At-Risk Pell Students (estimated)
Est At-Risk Pell Students = 
    ROUND(
        MAX(Enrollment[undergrad_enrollment]) * 
        MAX(FinancialAid[pell_pct_undergrad]) / 100 *
        (MAX(Retention[non_pell_retention]) - MAX(Retention[pell_retention])) / 100,
        0
    )
```

---

## Step 4 — Dashboard Pages

### Page 1: Overview
| Visual Type | Fields | Position |
|-------------|--------|----------|
| Card | `total_enrollment` (latest) | Top row |
| Card | `full_time_retention` (latest) | Top row |
| Card | `grad_6yr_rate` (latest) | Top row |
| Card | `Online %` measure | Top row |
| Card | `pell_pct_undergrad` (latest) | Top row |
| Stacked bar + Line | Year, UG + Grad enrollment, Total line | Center left |
| Area chart | Year, Online-only, On-campus | Center right |
| Multi-line | Year, all retention groups | Bottom left |
| Progress bars | KPI vs target measures | Bottom right |

### Page 2: Enrollment Deep Dive
| Visual | Fields |
|--------|--------|
| Line chart | Year, total / UG / Grad enrollment |
| Clustered bar | Year, Full-time vs Part-time |
| Multi-line | Year, female %, black %, hispanic % |
| Waterfall | Enrollment YoY Change |

### Page 3: Retention & Equity
| Visual | Fields |
|--------|--------|
| Multi-line | Year, all 5 retention groups |
| Grouped bar | Year, Pell gap, First-gen gap, FT/PT gap |
| KPI card | `Pell Equity Gap` measure |
| Scatter | `pell_retention` vs `non_pell_retention` |

### Page 4: Graduation
| Visual | Fields |
|--------|--------|
| Line + line | Cohort year, 6yr rate, 4yr rate |
| Constant line | 50% (HLC target) |
| Donut | 2017 cohort: grad / transfer / withdrew / enrolled |
| Table | All cohorts with rates |

### Page 5: IL Benchmarks
| Visual | Fields |
|--------|--------|
| Horizontal bar (sorted) | Institution, grad_rate_6yr |
| Horizontal bar (sorted) | Institution, retention_rate |
| Scatter | pell_grant_pct, grad_rate_6yr (size = enrollment) |
| Table | Full benchmark comparison |

### Page 6: Forecast (from `data/processed/enrollment_forecast_2024_2026.csv`)
| Visual | Fields |
|--------|--------|
| Line chart | Year, actual + 3 forecast scenarios |
| Error bars | CI lower/upper on baseline |
| Table | Scenario comparison |

---

## Step 5 — Formatting

**Theme colors:**
- Primary: `#003366` (UIS Blue)
- Accent: `#E84A27` (UIS Orange)
- Background: `#F3F2F1` (Power BI Grey)
- Cards: White with colored top border

**Typography:**
- Titles: Segoe UI, 14pt, Bold, UIS Blue
- Body: Segoe UI, 10pt, #4A5568

**Conditional Formatting on retention cards:**
- Green if value ≥ target
- Amber if within 5pp of target
- Red if more than 5pp below target

---

## Screenshots

See `docs/screenshots/` for full-resolution images of each dashboard page.

These screenshots were generated using Python/matplotlib to replicate the exact
Power BI Desktop visual layout, using the same data and color scheme.
