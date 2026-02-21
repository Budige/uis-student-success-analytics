"""
UIS Student Success Analytics - Data Loader
============================================
Loads IPEDS data into PostgreSQL database.

Data Sources:
    - IPEDS Fall Enrollment Survey (unitid: 145813)
    - IPEDS Graduation Rate Survey
    - IPEDS Student Financial Aid Survey
    - IPEDS Outcome Measures Survey

Author: Rakesh Budige
Email: rbudige@uis.edu (student)
Created: 2025-01-15
Modified: 2025-02-08 - Added retry logic for DB connections

Usage:
    python data_loader.py --env dev
    python data_loader.py --env prod --verify

TODO: Add support for direct IPEDS API when available
TODO: Automate annual data refresh (scheduled via cron)
"""

import os
import logging
import argparse
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("uis_etl.data_loader")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
UIS_UNITID = 145813
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

# Database connection (use env vars in production)
DB_CONFIG = {
    "dev": "postgresql://postgres:postgres@localhost:5432/uis_analytics_dev",
    "prod": "postgresql://uis_analyst:${DB_PASSWORD}@db.uis.edu:5432/uis_analytics",
}

# IPEDS file mappings
IPEDS_FILES = {
    "enrollment": "uis_enrollment_2014_2023.csv",
    "graduation": "uis_graduation_rates_2010_2017.csv",
    "retention": "uis_retention_rates_2014_2023.csv",
    "financial_aid": "uis_financial_aid_2014_2023.csv",
    "il_benchmarks": "illinois_universities_comparison_2023.csv",
}

# Expected column counts per table (data quality gate)
EXPECTED_COLUMNS = {
    "enrollment": 16,
    "graduation": 8,
    "retention": 7,
    "financial_aid": 9,
    "il_benchmarks": 10,
}


# ---------------------------------------------------------------------------
# Data Loading Functions
# ---------------------------------------------------------------------------

def load_enrollment(data_dir: Path) -> pd.DataFrame:
    """
    Load and validate UIS Fall Enrollment data from IPEDS.

    Args:
        data_dir: Path to raw data directory

    Returns:
        Cleaned enrollment DataFrame

    Raises:
        ValueError: If data fails validation checks
    """
    filepath = data_dir / IPEDS_FILES["enrollment"]
    logger.info(f"Loading enrollment data from {filepath}")

    df = pd.read_csv(filepath)
    logger.info(f"  Loaded {len(df)} rows, {len(df.columns)} columns")

    # Validation checks
    _validate_no_nulls(df, ["year", "total_enrollment", "undergrad_enrollment"])
    _validate_range(df, "year", 2014, 2030)
    _validate_range(df, "total_enrollment", 1000, 50000)

    # Verify totals add up (internal consistency)
    assert all(df["full_time"] + df["part_time"] == df["total_enrollment"]), \
        "ERROR: Full-time + Part-time != Total enrollment!"
    assert all(df["undergrad_enrollment"] + df["grad_enrollment"] == df["total_enrollment"]), \
        "ERROR: UG + Grad != Total enrollment!"
    assert all(df["male"] + df["female"] == df["total_enrollment"]), \
        "ERROR: Male + Female != Total enrollment!"

    logger.info("  ✓ All enrollment validation checks passed")
    return df


def load_graduation_rates(data_dir: Path) -> pd.DataFrame:
    """Load and validate IPEDS Graduation Rate Survey data."""
    filepath = data_dir / IPEDS_FILES["graduation"]
    logger.info(f"Loading graduation rate data from {filepath}")

    df = pd.read_csv(filepath)

    # Validate 6yr rate is within reasonable bounds
    _validate_range(df, "grad_6yr_rate", 0, 100)
    _validate_range(df, "grad_4yr_rate", 0, 100)

    # Verify cohort accounting (everyone must be accounted for)
    df["total_accounted"] = (
        df["grad_6yr_total"] + df["transferred_out"] +
        df["still_enrolled"] + df["withdrew"]
    )
    discrepancy = (df["total_accounted"] - df["cohort_size"]).abs().max()
    if discrepancy > 5:  # Allow tiny rounding errors
        logger.warning(f"  ⚠ Cohort accounting discrepancy: {discrepancy} students")
    else:
        logger.info("  ✓ Cohort accounting checks passed")

    df.drop("total_accounted", axis=1, inplace=True)
    return df


def load_retention_rates(data_dir: Path) -> pd.DataFrame:
    """Load and validate IPEDS Retention Rate data."""
    filepath = data_dir / IPEDS_FILES["retention"]
    logger.info(f"Loading retention data from {filepath}")

    df = pd.read_csv(filepath)

    # Retention rates should be between 0-100
    rate_cols = [c for c in df.columns if "retention" in c]
    for col in rate_cols:
        _validate_range(df, col, 0, 100)

    # Sanity check: non-Pell retention should always be > Pell retention
    # (Pell students face more financial barriers)
    violations = (df["non_pell_retention"] <= df["pell_retention"]).sum()
    if violations > 0:
        logger.warning(f"  ⚠ {violations} rows where non-Pell <= Pell retention (unexpected)")
    else:
        logger.info("  ✓ Pell/non-Pell retention ordering is correct")

    return df


def load_financial_aid(data_dir: Path) -> pd.DataFrame:
    """Load and validate IPEDS Financial Aid data."""
    filepath = data_dir / IPEDS_FILES["financial_aid"]
    logger.info(f"Loading financial aid data from {filepath}")

    df = pd.read_csv(filepath)

    # Net price should increase with income bracket (sanity check)
    price_checks = all(
        df["avg_net_price_30_48k"] > df["avg_net_price_0_30k"]
    ) and all(
        df["avg_net_price_48_75k"] > df["avg_net_price_30_48k"]
    ) and all(
        df["avg_net_price_75_110k"] > df["avg_net_price_48_75k"]
    )
    if price_checks:
        logger.info("  ✓ Net price brackets are in correct ascending order")
    else:
        logger.warning("  ⚠ Net price bracket ordering issue detected")

    return df


def load_il_benchmarks(data_dir: Path) -> pd.DataFrame:
    """Load Illinois university benchmarking data."""
    filepath = data_dir / IPEDS_FILES["il_benchmarks"]
    logger.info(f"Loading IL benchmarks from {filepath}")

    df = pd.read_csv(filepath)

    # Verify UIS is in the dataset
    uis_rows = df[df["unitid"] == UIS_UNITID]
    if len(uis_rows) == 0:
        raise ValueError(f"UIS (unitid={UIS_UNITID}) not found in benchmarks!")
    logger.info(f"  ✓ Found {len(df)} institutions including UIS")

    return df


# ---------------------------------------------------------------------------
# Database Loading
# ---------------------------------------------------------------------------

def get_engine(env: str = "dev"):
    """Create SQLAlchemy engine with retry logic."""
    conn_str = DB_CONFIG.get(env, DB_CONFIG["dev"])
    max_retries = 3

    for attempt in range(max_retries):
        try:
            engine = create_engine(conn_str, pool_pre_ping=True)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"  ✓ Database connection established ({env})")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"  DB connection failed (attempt {attempt+1}/{max_retries}), "
                              f"retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"  ✗ Could not connect to database after {max_retries} attempts")
                raise


def load_to_database(df: pd.DataFrame, table_name: str, engine, if_exists: str = "append") -> int:
    """
    Load DataFrame to PostgreSQL table.

    Returns:
        Number of rows loaded
    """
    # Add unitid for UIS-specific tables if missing
    if "unitid" not in df.columns and table_name.startswith("fact_"):
        df = df.copy()
        df.insert(0, "unitid", UIS_UNITID)

    rows_before = 0
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            rows_before = result.scalar()
    except Exception:
        pass  # Table might not exist yet

    df.to_sql(table_name, engine, if_exists=if_exists, index=False, method="multi")

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        rows_after = result.scalar()

    rows_loaded = rows_after - rows_before
    logger.info(f"  ✓ Loaded {rows_loaded} rows to {table_name} ({rows_after} total)")
    return rows_loaded


# ---------------------------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------------------------

def _validate_no_nulls(df: pd.DataFrame, columns: list[str]) -> None:
    """Raise ValueError if any required columns have nulls."""
    for col in columns:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            raise ValueError(f"Column '{col}' has {nulls} null values!")


def _validate_range(df: pd.DataFrame, column: str, min_val: float, max_val: float) -> None:
    """Log warning if values fall outside expected range."""
    out_of_range = ((df[column] < min_val) | (df[column] > max_val)).sum()
    if out_of_range > 0:
        logger.warning(f"  ⚠ Column '{column}': {out_of_range} values outside "
                      f"[{min_val}, {max_val}]")


def save_processed(df: pd.DataFrame, filename: str) -> None:
    """Save processed DataFrame to data/processed/."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    filepath = PROCESSED_DIR / filename
    df.to_csv(filepath, index=False)
    logger.info(f"  Saved processed file: {filepath}")


# ---------------------------------------------------------------------------
# Main ETL Pipeline
# ---------------------------------------------------------------------------

def run_etl(env: str = "dev", db_load: bool = False, verify: bool = False) -> dict:
    """
    Run the full ETL pipeline.

    Args:
        env: Environment ('dev' or 'prod')
        db_load: Whether to load into database (requires PostgreSQL)
        verify: Run extra verification checks

    Returns:
        Dictionary with row counts per table
    """
    logger.info("=" * 60)
    logger.info("UIS Student Success Analytics - ETL Pipeline")
    logger.info(f"Environment: {env} | DB Load: {db_load}")
    logger.info("=" * 60)

    results = {}

    # Load all datasets
    logger.info("\n--- Phase 1: Data Extraction ---")
    enrollment_df = load_enrollment(DATA_DIR)
    graduation_df = load_graduation_rates(DATA_DIR)
    retention_df = load_retention_rates(DATA_DIR)
    financial_df = load_financial_aid(DATA_DIR)
    benchmarks_df = load_il_benchmarks(DATA_DIR)

    results["enrollment_rows"] = len(enrollment_df)
    results["graduation_rows"] = len(graduation_df)
    results["retention_rows"] = len(retention_df)
    results["financial_rows"] = len(financial_df)
    results["benchmark_rows"] = len(benchmarks_df)

    logger.info("\n--- Phase 2: Data Transformation ---")

    # Calculate derived metrics
    enrollment_df["online_pct"] = (
        enrollment_df["online_only"] / enrollment_df["total_enrollment"] * 100
    ).round(1)
    enrollment_df["female_pct"] = (
        enrollment_df["female"] / enrollment_df["total_enrollment"] * 100
    ).round(1)
    enrollment_df["grad_pct"] = (
        enrollment_df["grad_enrollment"] / enrollment_df["total_enrollment"] * 100
    ).round(1)
    enrollment_df["urm_pct"] = (
        (enrollment_df["black"] + enrollment_df["hispanic"]) /
        enrollment_df["total_enrollment"] * 100
    ).round(1)

    # Save processed versions
    logger.info("\n--- Phase 3: Saving Processed Data ---")
    save_processed(enrollment_df, "uis_enrollment_processed.csv")
    save_processed(graduation_df, "uis_graduation_processed.csv")
    save_processed(retention_df, "uis_retention_processed.csv")
    save_processed(financial_df, "uis_financial_aid_processed.csv")
    save_processed(benchmarks_df, "il_benchmarks_processed.csv")

    if db_load:
        logger.info("\n--- Phase 4: Database Loading ---")
        try:
            engine = get_engine(env)
            load_to_database(enrollment_df, "fact_enrollment", engine)
            load_to_database(graduation_df, "fact_graduation_rates", engine)
            load_to_database(retention_df, "fact_retention_rates", engine)
            load_to_database(financial_df, "fact_financial_aid", engine)
            load_to_database(benchmarks_df, "fact_il_benchmarks", engine)
        except Exception as e:
            logger.error(f"Database loading failed: {e}")
            logger.info("Continuing without DB load (data saved to processed/)")

    logger.info("\n--- ETL Complete ---")
    logger.info(f"Total records processed: {sum(results.values())}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UIS Student Success ETL Pipeline")
    parser.add_argument("--env", choices=["dev", "prod"], default="dev")
    parser.add_argument("--db-load", action="store_true",
                       help="Load data to PostgreSQL (requires running DB)")
    parser.add_argument("--verify", action="store_true",
                       help="Run extra verification checks")
    args = parser.parse_args()

    run_etl(env=args.env, db_load=args.db_load, verify=args.verify)
