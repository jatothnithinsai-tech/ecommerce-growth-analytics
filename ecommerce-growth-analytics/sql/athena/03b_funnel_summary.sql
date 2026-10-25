-- Strict ordered, any-product, within-session funnel. Tracking gaps can affect losses.
SELECT COUNT(*) AS product_view_sessions,
 COUNT(cart_us) AS cart_sessions, COUNT(checkout_us) AS checkout_sessions,
 COUNT(purchase_us) AS purchase_sessions,
 COUNT(*) - COUNT(cart_us) AS view_to_cart_losses,
 COUNT(cart_us) - COUNT(checkout_us) AS cart_to_checkout_losses,
 COUNT(checkout_us) - COUNT(purchase_us) AS checkout_to_purchase_losses,
 ROUND(100.0 * COUNT(purchase_us) / NULLIF(COUNT(*), 0), 2) AS view_to_purchase_pct,
 COUNT_IF(cart_us <= view_us OR checkout_us <= cart_us OR purchase_us <= checkout_us) AS invalid_stage_order
FROM ga4_growth.session_funnel;
