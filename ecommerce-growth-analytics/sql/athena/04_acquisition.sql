-- First-user acquisition, not session attribution. Missing engagement flags are not explicit zeros.
SELECT first_user_source, first_user_medium,
 COUNT(*) AS sessions, COUNT(DISTINCT user_pseudo_id) AS observed_users,
 SUM(engaged_session) AS sessions_with_engagement_flag,
 SUM(has_purchase) AS purchasing_sessions,
 ROUND(100.0 * SUM(has_purchase) / COUNT(*), 2) AS session_purchase_pct
FROM ga4_growth.sessions
GROUP BY 1, 2 ORDER BY sessions DESC;
