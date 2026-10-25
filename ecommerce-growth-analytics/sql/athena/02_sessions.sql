-- Excludes unusable identifiers from session metrics; quantify exclusions separately.
-- Source/medium represent first-user acquisition, not session attribution.
CREATE OR REPLACE VIEW ga4_growth.sessions AS
SELECT user_pseudo_id, ga_session_id,
  MIN(event_date) AS session_date,
  MIN(event_timestamp) AS session_start_us,
  MAX(event_timestamp) AS session_end_us,
  MIN_BY(device_category, event_timestamp) AS device_category,
  MIN_BY(first_user_source, event_timestamp) AS first_user_source,
  MIN_BY(first_user_medium, event_timestamp) AS first_user_medium,
  COUNT(*) AS event_count,
  SUM(COALESCE(engagement_time_msec, 0)) AS engagement_time_msec,
  MAX(CASE WHEN session_engaged = '1' THEN 1 ELSE 0 END) AS engaged_session,
  MAX(CASE WHEN event_name = 'first_visit' THEN 1 ELSE 0 END) AS has_first_visit,
  MAX(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) AS has_purchase
FROM ga4_growth.events
WHERE user_pseudo_id IS NOT NULL AND ga_session_id IS NOT NULL
GROUP BY 1, 2;
