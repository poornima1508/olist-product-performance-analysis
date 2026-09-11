-- Monthly order count and revenue trend
-- Full raw output includes 2016-09 and 2016-12 (1 order each - test/seed rows)
-- and stops at 2018-08 (no delivered orders exist after this in the snapshot,
-- since later orders were still in transit/processing when the data was pulled).
-- The analysis layer (Python) filters this to the clean 2017-01 to 2018-08 window.

SELECT
  strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,
  COUNT(DISTINCT o.order_id) AS total_orders,
  ROUND(SUM(oi.price), 2) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY order_month
ORDER BY order_month;
