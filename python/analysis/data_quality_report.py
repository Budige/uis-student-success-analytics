"""
Data Quality Validation Report
================================
Validates all IPEDS datasets before analysis or DB loading.
Generates a quality report for OIRE data governance.

Author: Rakesh Budige
Created: 2025-01-18
Modified: 2025-02-01 - Added net price bracket ordering check
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
REPORT_DIR = Path(__file__).parent.parent.parent / "reports"


def run_quality_checks() -> dict:
    """Run all data quality checks. Returns dict of results."""
    results = {}
    all_passed = True

    print("=" * 60)
    print("UIS Student Success Analytics — Data Quality Report")
    print("=" * 60)

    # ── Enrollment ──────────────────────────────────────
    print("\n[1] Enrollment Data Checks")
    df = pd.read_csv(DATA_DIR / "uis_enrollment_2014_2023.csv")

    checks = {
        "Row count (expect 10)": len(df) == 10,
        "No null values": df.isnull().sum().sum() == 0,
        "FT + PT = Total": (df["full_time"] + df["part_time"] == df["total_enrollment"]).all(),
        "UG + Grad = Total": (df["undergrad_enrollment"] + df["grad_enrollment"] == df["total_enrollment"]).all(),
        "Male + Female = Total": (df["male"] + df["female"] == df["total_enrollment"]).all(),
        "Years are sequential": list(df["year"]) == list(range(2014, 2024)),
        "Enrollment > 0": (df["total_enrollment"] > 0).all(),
        "Online <= Total": (df["online_only"] <= df["total_enrollment"]).all(),
    }
    results["enrollment"] = checks
    for name, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        if not passed:
            all_passed = False
        print(f"  {status}: {name}")

    # ── Graduation ──────────────────────────────────────
    print("\n[2] Graduation Rate Checks")
    gdf = pd.read_csv(DATA_DIR / "uis_graduation_rates_2010_2017.csv")
    gdf["accounted"] = gdf["grad_6yr_total"] + gdf["transferred_out"] + gdf["still_enrolled"] + gdf["withdrew"]

    g_checks = {
        "Row count (expect 8)": len(gdf) == 8,
        "6yr rate 0-100": ((gdf["grad_6yr_rate"] >= 0) & (gdf["grad_6yr_rate"] <= 100)).all(),
        "4yr rate < 6yr rate": (gdf["grad_4yr_rate"] < gdf["grad_6yr_rate"]).all(),
        "Cohort accounting exact": (gdf["accounted"] == gdf["cohort_size"]).all(),
        "Improving trend": gdf["grad_6yr_rate"].is_monotonic_increasing,
    }
    results["graduation"] = g_checks
    for name, passed in g_checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        if not passed:
            all_passed = False
        print(f"  {status}: {name}")

    # ── Retention ───────────────────────────────────────
    print("\n[3] Retention Rate Checks")
    rdf = pd.read_csv(DATA_DIR / "uis_retention_rates_2014_2023.csv")

    r_checks = {
        "Row count (expect 10)": len(rdf) == 10,
        "Non-Pell > Pell retention": (rdf["non_pell_retention"] > rdf["pell_retention"]).all(),
        "Not-first-gen > First-gen": (rdf["not_first_gen_retention"] > rdf["first_gen_retention"]).all(),
        "Full-time > Part-time": (rdf["full_time_retention"] > rdf["part_time_retention"]).all(),
        "All rates 0-100": ((rdf.iloc[:, 1:] >= 0) & (rdf.iloc[:, 1:] <= 100)).all().all(),
        "Improving FT trend": rdf["full_time_retention"].is_monotonic_increasing,
    }
    results["retention"] = r_checks
    for name, passed in r_checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        if not passed:
            all_passed = False
        print(f"  {status}: {name}")

    # ── Financial Aid ────────────────────────────────────
    print("\n[4] Financial Aid Checks")
    fdf = pd.read_csv(DATA_DIR / "uis_financial_aid_2014_2023.csv")

    f_checks = {
        "Row count (expect 10)": len(fdf) == 10,
        "Net price brackets ascending": (
            (fdf["avg_net_price_30_48k"] > fdf["avg_net_price_0_30k"]).all() and
            (fdf["avg_net_price_48_75k"] > fdf["avg_net_price_30_48k"]).all() and
            (fdf["avg_net_price_75_110k"] > fdf["avg_net_price_48_75k"]).all()
        ),
        "Pell % reasonable (20-60%)": ((fdf["pell_pct_undergrad"] >= 20) & (fdf["pell_pct_undergrad"] <= 60)).all(),
        "Aid % <= 100": (fdf["any_aid_pct"] <= 100).all(),
        "Pell recipients > 0": (fdf["pell_recipients"] > 0).all(),
    }
    results["financial_aid"] = f_checks
    for name, passed in f_checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        if not passed:
            all_passed = False
        print(f"  {status}: {name}")

    # ── IL Benchmarks ────────────────────────────────────
    print("\n[5] IL Benchmarks Checks")
    bdf = pd.read_csv(DATA_DIR / "illinois_universities_comparison_2023.csv")

    b_checks = {
        "Row count (expect 9)": len(bdf) == 9,
        "UIS in dataset": (bdf["unitid"] == 145813).any(),
        "UIUC has highest grad rate": bdf.loc[bdf["grad_rate_6yr"].idxmax(), "institution"] == "U of I Urbana-Champaign",
        "No grad rate > 100": (bdf["grad_rate_6yr"] <= 100).all(),
        "Unique unitids": bdf["unitid"].nunique() == len(bdf),
    }
    results["il_benchmarks"] = b_checks
    for name, passed in b_checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        if not passed:
            all_passed = False
        print(f"  {status}: {name}")

    print("\n" + "=" * 60)
    total_checks = sum(len(v) for v in results.values())
    passed_checks = sum(sum(v.values()) for v in results.values())
    print(f"TOTAL: {passed_checks}/{total_checks} checks passed")
    if all_passed:
        print("✓ ALL CHECKS PASSED — Data is ready for analysis")
    else:
        print("✗ SOME CHECKS FAILED — Review data before proceeding")
    print("=" * 60)

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    run_quality_checks()
