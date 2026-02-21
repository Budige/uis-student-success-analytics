"""
Test suite for UIS Student Success Analytics data quality.
Run with: pytest tests/ -v

Author: Rakesh Budige
Created: 2025-01-22
"""

import pytest
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"


@pytest.fixture
def enrollment_df():
    return pd.read_csv(DATA_DIR / "uis_enrollment_2014_2023.csv")


@pytest.fixture
def graduation_df():
    return pd.read_csv(DATA_DIR / "uis_graduation_rates_2010_2017.csv")


@pytest.fixture
def retention_df():
    return pd.read_csv(DATA_DIR / "uis_retention_rates_2014_2023.csv")


@pytest.fixture
def financial_df():
    return pd.read_csv(DATA_DIR / "uis_financial_aid_2014_2023.csv")


@pytest.fixture
def benchmarks_df():
    return pd.read_csv(DATA_DIR / "illinois_universities_comparison_2023.csv")


class TestEnrollmentData:
    def test_row_count(self, enrollment_df):
        assert len(enrollment_df) == 10, "Expected 10 years of enrollment data"

    def test_no_nulls(self, enrollment_df):
        assert enrollment_df.isnull().sum().sum() == 0

    def test_ftpt_sums_to_total(self, enrollment_df):
        diff = (enrollment_df["full_time"] + enrollment_df["part_time"]
                - enrollment_df["total_enrollment"])
        assert diff.abs().max() == 0

    def test_ug_grad_sums_to_total(self, enrollment_df):
        diff = (enrollment_df["undergrad_enrollment"] + enrollment_df["grad_enrollment"]
                - enrollment_df["total_enrollment"])
        assert diff.abs().max() == 0

    def test_gender_sums_to_total(self, enrollment_df):
        diff = (enrollment_df["male"] + enrollment_df["female"]
                - enrollment_df["total_enrollment"])
        assert diff.abs().max() == 0

    def test_enrollment_range(self, enrollment_df):
        assert enrollment_df["total_enrollment"].min() > 3000
        assert enrollment_df["total_enrollment"].max() < 10000

    def test_online_increases_over_time(self, enrollment_df):
        """Online enrollment should generally increase over 10-year period."""
        first_3_avg = enrollment_df.head(3)["online_only"].mean()
        last_3_avg = enrollment_df.tail(3)["online_only"].mean()
        assert last_3_avg > first_3_avg


class TestGraduationData:
    def test_cohort_accounting(self, graduation_df):
        """All students in cohort must be accounted for."""
        accounted = (graduation_df["grad_6yr_total"] + graduation_df["transferred_out"]
                     + graduation_df["still_enrolled"] + graduation_df["withdrew"])
        diff = (accounted - graduation_df["cohort_size"]).abs()
        assert diff.max() == 0, f"Unaccounted students: max diff = {diff.max()}"

    def test_6yr_gt_4yr(self, graduation_df):
        assert (graduation_df["grad_6yr_rate"] > graduation_df["grad_4yr_rate"]).all()

    def test_improving_trend(self, graduation_df):
        """6yr grad rate should show overall improvement."""
        assert graduation_df["grad_6yr_rate"].iloc[-1] > graduation_df["grad_6yr_rate"].iloc[0]

    def test_rates_in_range(self, graduation_df):
        for col in ["grad_6yr_rate", "grad_4yr_rate"]:
            assert (graduation_df[col] >= 0).all()
            assert (graduation_df[col] <= 100).all()


class TestRetentionData:
    def test_pell_always_below_non_pell(self, retention_df):
        """Pell students historically have lower retention due to financial barriers."""
        assert (retention_df["non_pell_retention"] > retention_df["pell_retention"]).all()

    def test_fulltime_above_parttime(self, retention_df):
        assert (retention_df["full_time_retention"] > retention_df["part_time_retention"]).all()

    def test_equity_gap_reasonable(self, retention_df):
        """Pell-nonPell gap should be between 5 and 15 percentage points."""
        gap = retention_df["non_pell_retention"] - retention_df["pell_retention"]
        assert gap.min() >= 5
        assert gap.max() <= 15


class TestFinancialAidData:
    def test_net_price_bracket_order(self, financial_df):
        """Lower income brackets should have lower net price (more aid)."""
        assert (financial_df["avg_net_price_30_48k"] > financial_df["avg_net_price_0_30k"]).all()
        assert (financial_df["avg_net_price_48_75k"] > financial_df["avg_net_price_30_48k"]).all()
        assert (financial_df["avg_net_price_75_110k"] > financial_df["avg_net_price_48_75k"]).all()

    def test_pell_pct_reasonable(self, financial_df):
        """UIS Pell rate should be between 30-55% (access institution)."""
        assert financial_df["pell_pct_undergrad"].between(30, 55).all()


class TestBenchmarksData:
    def test_uis_present(self, benchmarks_df):
        assert (benchmarks_df["unitid"] == 145813).any()

    def test_uiuc_highest_grad_rate(self, benchmarks_df):
        top = benchmarks_df.loc[benchmarks_df["grad_rate_6yr"].idxmax(), "institution"]
        assert "Urbana" in top

    def test_all_rates_valid(self, benchmarks_df):
        for col in ["grad_rate_6yr", "retention_rate", "pell_grant_pct", "online_pct"]:
            assert (benchmarks_df[col] >= 0).all()
            assert (benchmarks_df[col] <= 100).all()
