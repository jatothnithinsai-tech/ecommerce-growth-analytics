-- First observed within the dataset, not first-ever customer activity.
WITH ranked_sessions AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY user_pseudo_id
      ORDER BY session_start_us, ga_session_id
    ) AS observed_session_number
  FROM ga4_growth.sessions
)
SELECT
  CASE WHEN observed_session_number = 1 THEN 'First observed session'
       ELSE 'Subsequent observed session' END AS session_segment,
  COUNT(*) AS sessions,
  COUNT(DISTINCT user_pseudo_id) AS observed_users,
  SUM(has_purchase) AS purchasing_sessions,
  ROUND(100.0 * SUM(has_purchase) / COUNT(*), 2) AS session_purchase_pct,
  ROUND(AVG(event_count), 2) AS avg_events_per_session
FROM ranked_sessions
GROUP BY 1
ORDER BY 1;
