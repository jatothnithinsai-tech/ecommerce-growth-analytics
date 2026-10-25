-- Query parameters: @start_suffix and @end_suffix (YYYYMMDD strings).
-- Scalar parameter extraction avoids expanding the items array.
-- No global deduplication: GA4 does not supply a universally unique event ID here.
SELECT
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  event_timestamp,
  event_name,
  user_pseudo_id,
  user_first_touch_timestamp,
  (SELECT ANY_VALUE(value.int_value) FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
  (SELECT ANY_VALUE(value.int_value) FROM UNNEST(event_params) WHERE key = 'engagement_time_msec') AS engagement_time_msec,
  (SELECT ANY_VALUE(COALESCE(value.string_value, CAST(value.int_value AS STRING)))
    FROM UNNEST(event_params) WHERE key = 'session_engaged') AS session_engaged,
  device.category AS device_category,
  geo.country AS country,
  traffic_source.source AS first_user_source,
  traffic_source.medium AS first_user_medium,
  traffic_source.name AS first_user_campaign,
  ecommerce.transaction_id,
  ecommerce.purchase_revenue_in_usd,
  ecommerce.refund_value_in_usd,
  ARRAY_LENGTH(items) AS item_entry_count
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN @start_suffix AND @end_suffix
