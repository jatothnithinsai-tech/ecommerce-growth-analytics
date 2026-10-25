-- First exploration: 1,000 unordered rows, not suitable for conversion estimates.
SELECT
  event_date,
  event_timestamp,
  event_name,
  user_pseudo_id,
  device.category AS device_category,
  geo.country AS country,
  traffic_source.source AS first_user_source,
  traffic_source.medium AS first_user_medium,
  ecommerce.transaction_id,
  ecommerce.purchase_revenue_in_usd
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_20201101`
LIMIT 1000;
