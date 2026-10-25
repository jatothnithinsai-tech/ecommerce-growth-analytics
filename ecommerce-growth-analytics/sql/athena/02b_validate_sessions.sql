SELECT
  COUNT(*) AS total_sessions,
  COUNT(DISTINCT user_pseudo_id) AS observed_users,
  SUM(event_count) AS events_in_sessions,
  SUM(has_purchase) AS purchasing_sessions,
  MIN(session_date) AS first_date,
  MAX(session_date) AS last_date,
  COUNT_IF(session_end_us < session_start_us) AS invalid_time_ranges
FROM ga4_growth.sessions;
