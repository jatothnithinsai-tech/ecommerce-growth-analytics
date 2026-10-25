-- Full-period quality check; expected 92 dates if every date has events.
-- Export results to data/quality/daily_event_coverage.csv.
-- Event counts are not user or session conversion rates.
SELECT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  COUNT(*) AS total_events,
  COUNT(DISTINCT user_pseudo_id) AS observed_users,
  COUNTIF(event_name = 'view_item') AS product_view_events,
  COUNTIF(event_name = 'add_to_cart') AS add_to_cart_events,
  COUNTIF(event_name = 'begin_checkout') AS checkout_events,
  COUNTIF(event_name = 'purchase') AS purchase_events,
  COUNTIF(user_pseudo_id IS NULL) AS missing_user_ids
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
GROUP BY 1
ORDER BY 1;
