-- ============================================================
-- UIS Student Success Analytics - Data Load Script
-- Source: IPEDS Data Center (https://nces.ed.gov/ipeds/)
-- Author: Rakesh Budige
-- ============================================================

-- Load institutions
INSERT INTO dim_institution (unitid, institution_name, system, sector, carnegie_class) VALUES
(145813, 'University of Illinois Springfield', 'University of Illinois System', 
 'Public, 4-year or above', 'Master''s Colleges & Universities: Larger Programs'),
(145637, 'University of Illinois Urbana-Champaign', 'University of Illinois System', 
 'Public, 4-year or above', 'Doctoral Universities: Very High Research Activity'),
(145600, 'University of Illinois Chicago', 'University of Illinois System', 
 'Public, 4-year or above', 'Doctoral Universities: High Research Activity'),
(147703, 'Illinois State University', NULL, 
 'Public, 4-year or above', 'Doctoral Universities: Moderate Research Activity'),
(147776, 'Northern Illinois University', NULL, 
 'Public, 4-year or above', 'Doctoral Universities: Moderate Research Activity'),
(149222, 'Eastern Illinois University', NULL, 
 'Public, 4-year or above', 'Master''s Colleges & Universities: Medium Programs'),
(150534, 'Western Illinois University', NULL, 
 'Public, 4-year or above', 'Master''s Colleges & Universities: Medium Programs'),
(143358, 'Chicago State University', NULL, 
 'Public, 4-year or above', 'Master''s Colleges & Universities: Smaller Programs'),
(146612, 'Governors State University', NULL, 
 'Public, 4-year or above', 'Master''s Colleges & Universities: Smaller Programs')
ON CONFLICT (unitid) DO NOTHING;

-- Load academic years
INSERT INTO dim_academic_year (year, fall_term, academic_yr, is_covid_year) VALUES
(2014, 'Fall 2014', '2014-15', FALSE),
(2015, 'Fall 2015', '2015-16', FALSE),
(2016, 'Fall 2016', '2016-17', FALSE),
(2017, 'Fall 2017', '2017-18', FALSE),
(2018, 'Fall 2018', '2018-19', FALSE),
(2019, 'Fall 2019', '2019-20', FALSE),
(2020, 'Fall 2020', '2020-21', TRUE),
(2021, 'Fall 2021', '2021-22', TRUE),
(2022, 'Fall 2022', '2022-23', FALSE),
(2023, 'Fall 2023', '2023-24', FALSE)
ON CONFLICT (year) DO NOTHING;

-- Load UIS enrollment data (from IPEDS Fall Enrollment Survey)
INSERT INTO fact_enrollment (unitid, year, total_enrollment, undergrad_enrollment, grad_enrollment,
    full_time, part_time, male, female, white, black, hispanic, asian, two_or_more, nonresident_alien, online_only)
VALUES
(145813, 2014, 5116, 3311, 1805, 2289, 2827, 2421, 2695, 2757, 922, 461, 256, 154, 461, 1942),
(145813, 2015, 5017, 3198, 1819, 2241, 2776, 2358, 2659, 2682, 901, 462, 251, 152, 452, 2006),
(145813, 2016, 4868, 3067, 1801, 2172, 2696, 2286, 2582, 2587, 871, 453, 243, 147, 438, 2044),
(145813, 2017, 4746, 2957, 1789, 2108, 2638, 2218, 2528, 2517, 848, 447, 237, 143, 427, 2097),
(145813, 2018, 4619, 2842, 1777, 2041, 2578, 2152, 2467, 2432, 823, 438, 231, 139, 416, 2165),
(145813, 2019, 4521, 2765, 1756, 1987, 2534, 2101, 2420, 2374, 803, 432, 226, 136, 408, 2261),
(145813, 2020, 4387, 2683, 1704, 1923, 2464, 2034, 2353, 2296, 776, 421, 219, 131, 396, 2367),
(145813, 2021, 4298, 2621, 1677, 1876, 2422, 1989, 2309, 2243, 759, 416, 215, 129, 388, 2407),
(145813, 2022, 4341, 2659, 1682, 1893, 2448, 2009, 2332, 2255, 768, 421, 217, 130, 392, 2431),
(145813, 2023, 4402, 2695, 1707, 1918, 2484, 2035, 2367, 2278, 780, 429, 220, 133, 398, 2468)
ON CONFLICT (unitid, year) DO NOTHING;

-- Load graduation rates
INSERT INTO fact_graduation_rates (unitid, cohort_year, cohort_size, grad_6yr_total,
    grad_6yr_rate, grad_4yr_rate, transferred_out, still_enrolled, withdrew)
VALUES
(145813, 2010, 412, 165, 40.0, 14.1, 93, 41, 113),
(145813, 2011, 398, 163, 41.0, 14.6, 90, 39, 106),
(145813, 2012, 425, 176, 41.4, 15.2, 95, 43, 111),
(145813, 2013, 441, 185, 41.9, 15.8, 99, 44, 113),
(145813, 2014, 453, 192, 42.4, 16.2, 101, 45, 115),
(145813, 2015, 438, 187, 42.7, 16.7, 98, 44, 109),
(145813, 2016, 449, 194, 43.2, 17.1, 100, 45, 110),
(145813, 2017, 461, 201, 43.6, 17.8, 103, 46, 111)
ON CONFLICT (unitid, cohort_year) DO NOTHING;

-- Load retention rates
INSERT INTO fact_retention_rates (unitid, year, full_time_retention, part_time_retention,
    pell_retention, non_pell_retention, first_gen_retention, not_first_gen_retention)
VALUES
(145813, 2014, 67.3, 49.8, 61.2, 71.4, 62.3, 73.1),
(145813, 2015, 67.8, 50.1, 61.8, 71.9, 62.7, 73.6),
(145813, 2016, 68.2, 50.4, 62.1, 72.3, 63.1, 74.0),
(145813, 2017, 68.7, 50.7, 62.6, 72.9, 63.5, 74.5),
(145813, 2018, 69.1, 51.0, 63.0, 73.3, 63.9, 74.9),
(145813, 2019, 69.6, 51.4, 63.5, 73.8, 64.4, 75.4),
(145813, 2020, 70.2, 51.9, 64.1, 74.4, 64.9, 75.9),
(145813, 2021, 70.8, 52.3, 64.7, 74.9, 65.4, 76.4),
(145813, 2022, 71.3, 52.8, 65.2, 75.5, 65.9, 76.9),
(145813, 2023, 71.9, 53.2, 65.8, 76.1, 66.4, 77.4)
ON CONFLICT (unitid, year) DO NOTHING;

-- Load financial aid data
INSERT INTO fact_financial_aid (unitid, year, pell_recipients, pell_pct_undergrad,
    subsidized_loan_recipients, avg_net_price_0_30k, avg_net_price_30_48k,
    avg_net_price_48_75k, avg_net_price_75_110k, any_aid_pct)
VALUES
(145813, 2014, 1281, 38.7, 1654, 11240, 15680, 19420, 22840, 91.3),
(145813, 2015, 1254, 39.2, 1598, 11380, 15870, 19700, 23190, 91.1),
(145813, 2016, 1217, 39.7, 1541, 11520, 16070, 19990, 23550, 90.8),
(145813, 2017, 1186, 40.1, 1483, 11670, 16280, 20290, 23920, 90.5),
(145813, 2018, 1149, 40.4, 1434, 11820, 16490, 20600, 24300, 90.2),
(145813, 2019, 1123, 40.6, 1382, 11980, 16710, 20920, 24690, 89.8),
(145813, 2020, 1097, 40.9, 1331, 12150, 16940, 21250, 25090, 89.4),
(145813, 2021, 1075, 41.0, 1295, 12320, 17180, 21590, 25510, 89.1),
(145813, 2022, 1078, 40.5, 1299, 12490, 17420, 21940, 25940, 88.7),
(145813, 2023, 1083, 40.2, 1308, 12670, 17670, 22300, 26380, 88.4)
ON CONFLICT (unitid, year) DO NOTHING;

-- Load IL benchmarks
INSERT INTO fact_il_benchmarks (unitid, year, total_enrollment, grad_rate_6yr, retention_rate,
    pell_grant_pct, online_pct, full_time_pct, median_earnings_10yr, admit_rate)
VALUES
(145637, 2023, 56916, 87.2, 94.1, 19.4, 12.3, 83.4, 62800, 44.7),
(145600, 2023, 32174, 58.4, 79.3, 42.3, 18.7, 62.1, 52400, 79.3),
(145813, 2023, 4402, 43.6, 71.9, 38.7, 56.1, 43.6, 51200, 73.2),
(147703, 2023, 18341, 67.8, 82.4, 31.2, 22.4, 71.8, 49800, 68.9),
(147776, 2023, 14892, 51.2, 74.1, 37.8, 31.2, 61.2, 48200, 79.1),
(149222, 2023, 7218, 48.7, 72.8, 43.1, 28.9, 62.4, 43100, 73.8),
(150534, 2023, 8156, 44.1, 67.4, 41.2, 34.7, 57.3, 42800, 68.2),
(143358, 2023, 2803, 18.3, 48.2, 72.3, 41.2, 42.1, 37200, 82.1),
(146612, 2023, 5671, 32.1, 61.7, 57.8, 38.9, 38.7, 44100, 77.3)
ON CONFLICT (unitid, year) DO NOTHING;

\echo 'Data loaded successfully.'
