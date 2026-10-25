-- Observed strict ordered funnel. Denominator: product-view sessions.
SELECT
  s.device_category,
  COUNT(*) AS product_view_sessions,
  COUNT(f.cart_us) AS cart_sessions,
  COUNT(f.checkout_us) AS checkout_sessions,
  COUNT(f.purchase_us) AS purchase_sessions,
  ROUND(100.0 * COUNT(f.cart_us) / COUNT(*), 2) AS view_to_cart_pct,
  ROUND(100.0 * COUNT(f.purchase_us) / COUNT(*), 2) AS view_to_purchase_pct
FROM ga4_growth.session_funnel f
JOIN ga4_growth.sessions s
  ON f.user_pseudo_id = s.user_pseudo_id
  AND f.ga_session_id = s.ga_session_id
GROUP BY s.device_category
ORDER BY product_view_sessions DESC;
