-- Underperforming products: those that sold exactly once in the entire
-- ~2-year dataset window, broken down by category.
-- (Products that never sold at all are already excluded from total_products_sold
-- in the core KPI query - roughly 735 of the 32,951 catalog products.)

WITH product_orders AS (
  SELECT oi.product_id, COUNT(DISTINCT oi.order_id) AS order_count
  FROM orders o
  JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY oi.product_id
)
SELECT
  COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
  COUNT(*) AS underperforming_products
FROM product_orders po
JOIN products p ON po.product_id = p.product_id
LEFT JOIN product_category_name_translation t
  ON p.product_category_name = t.product_category_name
WHERE po.order_count = 1
GROUP BY category
ORDER BY underperforming_products DESC;
