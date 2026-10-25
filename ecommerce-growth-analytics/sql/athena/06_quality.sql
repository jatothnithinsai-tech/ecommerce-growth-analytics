-- Record counts and missing identifiers.
SELECT event_date, COUNT(*) AS event_rows,
 COUNT_IF(user_pseudo_id IS NULL) AS missing_user,
 COUNT_IF(ga_session_id IS NULL) AS missing_session
FROM ga4_growth.events GROUP BY 1 ORDER BY 1;

-- Inspect duplicates globally before deciding on a transaction policy.
SELECT transaction_id, COUNT(*) AS purchase_rows,
 MIN(purchase_revenue_in_usd) AS min_revenue_usd,
 MAX(purchase_revenue_in_usd) AS max_revenue_usd
FROM ga4_growth.events
WHERE event_name = 'purchase' AND transaction_id IS NOT NULL
GROUP BY 1 HAVING COUNT(*) > 1;

-- Raw recorded purchase revenue, before transaction deduplication or refunds.
SELECT SUM(purchase_revenue_in_usd) AS raw_purchase_revenue_usd,
 COUNT_IF(transaction_id IS NULL) AS missing_transaction_ids
FROM ga4_growth.events WHERE event_name = 'purchase';

-- Should return zero violations.
SELECT COUNT(*) AS funnel_order_violations FROM ga4_growth.session_funnel
WHERE cart_us <= view_us OR checkout_us <= cart_us OR purchase_us <= checkout_us;
