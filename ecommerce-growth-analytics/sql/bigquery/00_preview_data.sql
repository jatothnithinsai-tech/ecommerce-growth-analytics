-- Run in BigQuery SQL workspace. Preview only; not a complete extract.
SELECT
  event_date,
  event_timestamp,
  event_name,
  user_pseudo_id,
  (SELECT ANY_VALUE(value.int_value) FROM UNNEST(event_params)
   WHERE key = 'ga_session_id') AS ga_session_id,
  device.category AS device_category,
  geo.country AS country,
  traffic_source.source AS first_user_source,
  traffic_source.medium AS first_user_medium,
  ecommerce.transaction_id,
  ecommerce.purchase_revenue_in_usd
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_20201101`
LIMIT 1000;
