# Data Sources Documentation

## IPEDS Data Sources

All data downloaded from the IPEDS Data Center:
https://nces.ed.gov/ipeds/datacenter/

### University of Illinois Springfield (Unit ID: 145813)

| File | IPEDS Survey | Collection Period |
|------|-------------|-------------------|
| uis_enrollment_2014_2023.csv | Fall Enrollment (EF) | Fall 2014 – Fall 2023 |
| uis_graduation_rates_2010_2017.csv | Graduation Rate (GR) | 2010–2017 cohorts |
| uis_retention_rates_2014_2023.csv | Fall Enrollment – Retention | 2014–2023 |
| uis_financial_aid_2014_2023.csv | Student Financial Aid (SFA) | 2014–2023 |

### Illinois Peer Institutions

| File | Sources | Year |
|------|---------|------|
| illinois_universities_comparison_2023.csv | IPEDS DataCenter + College Scorecard | 2023 |

## Notes on Data Fields

**unknown_race in enrollment data**: The difference between the sum of all 
race/ethnicity categories and total enrollment represents students who chose 
not to report race or whose race is not categorized. This is standard in 
IPEDS reporting (typically 2-4% of enrollment).

**6-year graduation rate**: Measured at 150% of normal time (6 years for a 
4-year program). The IPEDS Graduation Rate Survey tracks first-time, full-time 
degree-seeking students in the cohort who graduate within 6 years.

**Retention rate**: Percentage of first-time degree-seeking students who enrolled 
in the fall following their first enrollment. Full-time and part-time rates are 
reported separately per IPEDS methodology.

## Downloading Fresh Data

1. Go to: https://nces.ed.gov/ipeds/datacenter/
2. Search for institution: "University of Illinois at Springfield" 
3. Unit ID: 145813
4. Select surveys: Fall Enrollment, Graduation Rate, SFA
5. Download as CSV
