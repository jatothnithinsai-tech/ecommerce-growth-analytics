-- This classification describes observed sessions, not verified customer tenure.
WITH first_sessions AS (
 SELECT user_pseudo_id, MIN(session_start_us) AS first_observed_start
 FROM ga4_growth.sessions GROUP BY 1
)
SELECT CASE WHEN s.has_first_visit = 1 THEN 'first_visit_signal'
 WHEN s.session_start_us = f.first_observed_start THEN 'first_observed_without_signal'
 ELSE 'subsequent_observed_session' END AS user_session_segment,
 COUNT(*) AS sessions, SUM(s.has_purchase) AS purchasing_sessions,
 1.0 * SUM(s.has_purchase) / COUNT(*) AS session_purchase_rate
FROM ga4_growth.sessions s JOIN first_sessions f ON s.user_pseudo_id = f.user_pseudo_id
GROUP BY 1;
