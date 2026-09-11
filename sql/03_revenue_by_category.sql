-- Revenue and order count by category (all categories, ranked by revenue)
-- LEFT JOIN + COALESCE used so products with a missing/untranslated category
-- still appear (as 'unknown') instead of silently dropping out of the results.

SELECT
  COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
  COUNT(DISTINCT oi.order_id) AS total_orders,
  ROUND(SUM(oi.price), 2) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t
  ON p.product_category_name = t.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY total_revenue DESC;
