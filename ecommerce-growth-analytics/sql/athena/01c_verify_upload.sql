-- Expected: 4295584 rows, 92 dates, 2020-11-01 to 2021-01-31.
-- Result saved in data/quality/athena_upload_verification.csv.
SELECT
  COUNT(*) AS total_events,
  COUNT(DISTINCT event_date) AS total_days,
  MIN(event_date) AS first_date,
  MAX(event_date) AS last_date
FROM ga4_growth.events;
