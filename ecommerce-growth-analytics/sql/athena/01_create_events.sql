-- Matches the actual uploaded Parquet schema. Execute in eu-north-1.
CREATE EXTERNAL TABLE IF NOT EXISTS ga4_growth.events (
  source_file STRING,
  source_row_number BIGINT,
  event_timestamp BIGINT,
  event_name STRING,
  user_pseudo_id STRING,
  user_first_touch_timestamp BIGINT,
  ga_session_id STRING,
  engagement_time_msec BIGINT,
  session_engaged STRING,
  device_category STRING,
  country STRING,
  first_user_source STRING,
  first_user_medium STRING,
  transaction_id STRING,
  purchase_revenue_in_usd DOUBLE,
  refund_value_in_usd DOUBLE,
  event_time_utc STRING,
  session_key STRING
)
PARTITIONED BY (event_date STRING)
STORED AS PARQUET
LOCATION 's3://ecommerce-growth-analytics-20261024-nsj/Data/aws_ready/';
