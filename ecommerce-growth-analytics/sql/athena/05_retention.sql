-- First-observed cohorts, Monday weeks, excludes partial opening cohort.
-- Completed zero-activity weeks retained; immature follow-up weeks excluded.
WITH activity AS (
 SELECT DISTINCT user_pseudo_id,
 CAST(DATE_TRUNC('week', CAST(event_date AS DATE)) AS DATE) AS activity_week
 FROM ga4_growth.events WHERE user_pseudo_id IS NOT NULL
), cohorts AS (
 SELECT user_pseudo_id, MIN(activity_week) AS cohort_week FROM activity GROUP BY 1
), cohort_sizes AS (
 SELECT cohort_week, COUNT(*) AS cohort_users FROM cohorts GROUP BY 1
), bounds AS (
 SELECT MIN(CAST(event_date AS DATE)) AS first_date,
 MAX(CAST(event_date AS DATE)) AS last_date FROM ga4_growth.events
), eligible_weeks AS (
 SELECT s.cohort_week, s.cohort_users, week_number,
 DATE_ADD('week', week_number, s.cohort_week) AS activity_week
 FROM cohort_sizes s CROSS JOIN bounds b
 CROSS JOIN UNNEST(SEQUENCE(CAST(0 AS BIGINT),
 DATE_DIFF('week', s.cohort_week, CAST(DATE_TRUNC('week', b.last_date) AS DATE)))) AS t(week_number)
 WHERE s.cohort_week >= b.first_date
 AND DATE_ADD('day', 6, DATE_ADD('week', week_number, s.cohort_week)) <= b.last_date
), active_counts AS (
 SELECT c.cohort_week, a.activity_week, COUNT(*) AS active_users
 FROM cohorts c JOIN activity a ON c.user_pseudo_id = a.user_pseudo_id GROUP BY 1, 2
)
SELECT e.cohort_week, e.activity_week, e.week_number, e.cohort_users,
 COALESCE(a.active_users, 0) AS active_users,
 ROUND(100.0 * COALESCE(a.active_users, 0) / e.cohort_users, 2) AS retention_pct
FROM eligible_weeks e LEFT JOIN active_counts a
 ON e.cohort_week = a.cohort_week AND e.activity_week = a.activity_week
ORDER BY e.cohort_week, e.week_number;
