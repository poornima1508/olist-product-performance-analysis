-- Core KPIs: total orders, products sold, revenue, average order value
-- Filtered to delivered orders only (canceled/unavailable orders never generated real revenue)

SELECT
  COUNT(DISTINCT o.order_id) AS total_orders,
  COUNT(DISTINCT oi.product_id) AS total_products_sold,
  ROUND(SUM(oi.price), 2) AS total_revenue,
  ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered';
