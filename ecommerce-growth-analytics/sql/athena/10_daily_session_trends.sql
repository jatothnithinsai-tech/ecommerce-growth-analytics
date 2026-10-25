-- Session start date; daily distinct users are not additive across dates.
SELECT session_date, COUNT(*) AS sessions,
 COUNT(DISTINCT user_pseudo_id) AS observed_users,
 SUM(has_purchase) AS purchasing_sessions,
 SUM(engaged_session) AS sessions_with_engagement_flag,
 ROUND(100.0 * SUM(has_purchase) / COUNT(*), 2) AS session_purchase_pct
FROM ga4_growth.sessions GROUP BY session_date ORDER BY session_date;
