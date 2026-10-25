-- Python template: {date_suffix} is replaced with a validated YYYYMMDD date.
-- Complete-day CSV export used for the current raw dataset. No row limit.
-- Source reporting date is distinct from UTC timestamp date.
SELECT
  event_date,
  event_timestamp,
  event_name,
  user_pseudo_id,
  user_first_touch_timestamp,
  (SELECT ANY_VALUE(value.int_value) FROM UNNEST(event_params)
    WHERE key = 'ga_session_id') AS ga_session_id,
  (SELECT ANY_VALUE(value.int_value) FROM UNNEST(event_params)
    WHERE key = 'engagement_time_msec') AS engagement_time_msec,
  (SELECT ANY_VALUE(COALESCE(value.string_value, CAST(value.int_value AS STRING)))
    FROM UNNEST(event_params) WHERE key = 'session_engaged') AS session_engaged,
  device.category AS device_category,
  geo.country AS country,
  traffic_source.source AS first_user_source,
  traffic_source.medium AS first_user_medium,
  ecommerce.transaction_id,
  ecommerce.purchase_revenue_in_usd,
  ecommerce.refund_value_in_usd
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_{date_suffix}`;
