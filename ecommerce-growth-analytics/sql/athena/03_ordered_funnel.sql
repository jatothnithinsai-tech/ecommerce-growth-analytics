-- Strictly increasing timestamps, same user/session, any product.
-- Tied timestamps cannot establish order and are excluded from subsequent stages.
CREATE OR REPLACE VIEW ga4_growth.session_funnel AS
WITH views AS (
 SELECT user_pseudo_id, ga_session_id, MIN(event_timestamp) AS view_us
 FROM ga4_growth.events
 WHERE event_name = 'view_item' AND user_pseudo_id IS NOT NULL AND ga_session_id IS NOT NULL
 GROUP BY 1, 2
), carts AS (
 SELECT v.user_pseudo_id, v.ga_session_id, v.view_us,
   MIN(e.event_timestamp) AS cart_us
 FROM views v LEFT JOIN ga4_growth.events e
 ON e.user_pseudo_id = v.user_pseudo_id AND e.ga_session_id = v.ga_session_id
 AND e.event_name = 'add_to_cart' AND e.event_timestamp > v.view_us
 GROUP BY 1, 2, 3
), checkouts AS (
 SELECT c.user_pseudo_id, c.ga_session_id, c.view_us, c.cart_us,
   MIN(e.event_timestamp) AS checkout_us
 FROM carts c LEFT JOIN ga4_growth.events e
 ON e.user_pseudo_id = c.user_pseudo_id AND e.ga_session_id = c.ga_session_id
 AND e.event_name = 'begin_checkout' AND e.event_timestamp > c.cart_us
 GROUP BY 1, 2, 3, 4
)
SELECT c.user_pseudo_id, c.ga_session_id, c.view_us, c.cart_us, c.checkout_us,
 MIN(e.event_timestamp) AS purchase_us
FROM checkouts c LEFT JOIN ga4_growth.events e
ON e.user_pseudo_id = c.user_pseudo_id AND e.ga_session_id = c.ga_session_id
AND e.event_name = 'purchase' AND e.event_timestamp > c.checkout_us
GROUP BY 1, 2, 3, 4, 5;
