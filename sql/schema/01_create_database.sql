-- ============================================================
-- UIS Student Success Analytics - Database Schema
-- University of Illinois Springfield (Unit ID: 145813)
-- Data Source: IPEDS (Integrated Postsecondary Education Data System)
-- Author: Rakesh Budige
-- Created: 2025-01-15
-- Purpose: Support OIRE reporting, compliance, and strategic planning
-- ============================================================

-- NOTE: Run this as postgres superuser
-- \c uis_analytics

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_institution (
    institution_id      SERIAL PRIMARY KEY,
    unitid              INTEGER UNIQUE NOT NULL,  -- IPEDS Unit ID
    institution_name    VARCHAR(200) NOT NULL,
    system              VARCHAR(100),  -- e.g., 'University of Illinois System'
    state               CHAR(2) DEFAULT 'IL',
    sector              VARCHAR(50),   -- e.g., 'Public, 4-year or above'
    hbcu_flag           BOOLEAN DEFAULT FALSE,
    tribal_flag         BOOLEAN DEFAULT FALSE,
    carnegie_class      VARCHAR(100),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_academic_year (
    year_id     SERIAL PRIMARY KEY,
    year        INTEGER UNIQUE NOT NULL,
    fall_term   VARCHAR(20),   -- e.g., 'Fall 2023'
    academic_yr VARCHAR(20),   -- e.g., '2023-24'
    is_covid_year BOOLEAN DEFAULT FALSE  -- Flag for 2020-2021
);

CREATE TABLE IF NOT EXISTS dim_student_type (
    type_id         SERIAL PRIMARY KEY,
    type_code       VARCHAR(20) UNIQUE NOT NULL,
    type_name       VARCHAR(100),
    level_of_study  VARCHAR(50),  -- Undergraduate / Graduate
    attendance_status VARCHAR(50) -- Full-time / Part-time
);

CREATE TABLE IF NOT EXISTS dim_race_ethnicity (
    race_id         SERIAL PRIMARY KEY,
    race_code       VARCHAR(30) UNIQUE NOT NULL,
    race_name       VARCHAR(100),
    ipeds_category  VARCHAR(100)  -- Official IPEDS race/ethnicity category
);

-- ============================================================
-- FACT TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_enrollment (
    enrollment_id           BIGSERIAL PRIMARY KEY,
    unitid                  INTEGER NOT NULL REFERENCES dim_institution(unitid),
    year                    INTEGER NOT NULL,
    total_enrollment        INTEGER,
    undergrad_enrollment    INTEGER,
    grad_enrollment         INTEGER,
    full_time               INTEGER,
    part_time               INTEGER,
    male                    INTEGER,
    female                  INTEGER,
    white                   INTEGER,
    black                   INTEGER,
    hispanic                INTEGER,
    asian                   INTEGER,
    two_or_more             INTEGER,
    nonresident_alien       INTEGER,
    online_only             INTEGER,
    data_source             VARCHAR(50) DEFAULT 'IPEDS Fall Enrollment',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unitid, year)
);

CREATE TABLE IF NOT EXISTS fact_graduation_rates (
    grad_id         BIGSERIAL PRIMARY KEY,
    unitid          INTEGER NOT NULL REFERENCES dim_institution(unitid),
    cohort_year     INTEGER NOT NULL,
    cohort_size     INTEGER,
    grad_6yr_total  INTEGER,
    grad_6yr_rate   DECIMAL(5,2),
    grad_4yr_rate   DECIMAL(5,2),
    transferred_out INTEGER,
    still_enrolled  INTEGER,
    withdrew        INTEGER,
    data_source     VARCHAR(50) DEFAULT 'IPEDS Graduation Rate Survey',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unitid, cohort_year)
);

CREATE TABLE IF NOT EXISTS fact_retention_rates (
    retention_id            BIGSERIAL PRIMARY KEY,
    unitid                  INTEGER NOT NULL REFERENCES dim_institution(unitid),
    year                    INTEGER NOT NULL,
    full_time_retention     DECIMAL(5,2),
    part_time_retention     DECIMAL(5,2),
    pell_retention          DECIMAL(5,2),
    non_pell_retention      DECIMAL(5,2),
    first_gen_retention     DECIMAL(5,2),
    not_first_gen_retention DECIMAL(5,2),
    data_source             VARCHAR(50) DEFAULT 'IPEDS Fall Enrollment',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unitid, year)
);

CREATE TABLE IF NOT EXISTS fact_financial_aid (
    aid_id                      BIGSERIAL PRIMARY KEY,
    unitid                      INTEGER NOT NULL REFERENCES dim_institution(unitid),
    year                        INTEGER NOT NULL,
    pell_recipients             INTEGER,
    pell_pct_undergrad          DECIMAL(5,2),
    subsidized_loan_recipients  INTEGER,
    avg_net_price_0_30k         DECIMAL(10,2),
    avg_net_price_30_48k        DECIMAL(10,2),
    avg_net_price_48_75k        DECIMAL(10,2),
    avg_net_price_75_110k       DECIMAL(10,2),
    any_aid_pct                 DECIMAL(5,2),
    data_source                 VARCHAR(50) DEFAULT 'IPEDS Student Financial Aid',
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unitid, year)
);

CREATE TABLE IF NOT EXISTS fact_il_benchmarks (
    benchmark_id        BIGSERIAL PRIMARY KEY,
    unitid              INTEGER NOT NULL REFERENCES dim_institution(unitid),
    year                INTEGER NOT NULL,
    total_enrollment    INTEGER,
    grad_rate_6yr       DECIMAL(5,2),
    retention_rate      DECIMAL(5,2),
    pell_grant_pct      DECIMAL(5,2),
    online_pct          DECIMAL(5,2),
    full_time_pct       DECIMAL(5,2),
    median_earnings_10yr DECIMAL(10,2),
    admit_rate          DECIMAL(5,2),
    data_source         VARCHAR(50) DEFAULT 'IPEDS + College Scorecard',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unitid, year)
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX idx_enrollment_year ON fact_enrollment(year);
CREATE INDEX idx_enrollment_unitid ON fact_enrollment(unitid);
CREATE INDEX idx_graduation_cohort ON fact_graduation_rates(cohort_year);
CREATE INDEX idx_retention_year ON fact_retention_rates(year);
CREATE INDEX idx_financial_year ON fact_financial_aid(year);

-- ============================================================
-- AUDIT LOG TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_log (
    log_id      BIGSERIAL PRIMARY KEY,
    table_name  VARCHAR(100),
    operation   VARCHAR(20),
    changed_by  VARCHAR(100),
    changed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_count   INTEGER,
    notes       VARCHAR(500)
);

-- TODO: Add triggers for audit logging on fact tables
-- TODO: Consider partitioning fact_enrollment by year for performance

COMMENT ON TABLE fact_enrollment IS 'IPEDS Fall Enrollment Survey data - headcount by demographic';
COMMENT ON TABLE fact_graduation_rates IS 'IPEDS Graduation Rate Survey - 150% of normal time completers';
COMMENT ON TABLE fact_retention_rates IS 'IPEDS retention rates by enrollment status and demographics';
COMMENT ON TABLE fact_financial_aid IS 'IPEDS Student Financial Aid Survey - Pell, loans, net price';
COMMENT ON TABLE fact_il_benchmarks IS 'Peer institution benchmarking for Illinois public universities';

\echo 'Schema created successfully. Run 02_load_data.sql next.'
