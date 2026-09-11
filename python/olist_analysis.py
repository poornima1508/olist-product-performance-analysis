"""
Olist Product Performance Analysis
Connects to the Olist SQLite database, runs the core analysis queries,
adds derived metrics (growth %), and exports clean CSVs for Power BI.
"""

import sqlite3
import pandas as pd
import os

# ---- Setup ----
DB_PATH = os.path.expanduser("~/Downloads/olist.sqlite")
OUTPUT_DIR = os.path.expanduser("~/Downloads/olist_exports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
print(f"Connected to {DB_PATH}")

# ---- 1. Core KPIs ----
kpi_query = """
SELECT
  COUNT(DISTINCT o.order_id) AS total_orders,
  COUNT(DISTINCT oi.product_id) AS total_products_sold,
  ROUND(SUM(oi.price), 2) AS total_revenue,
  ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered';
"""
df_kpi = pd.read_sql_query(kpi_query, conn)
df_kpi.to_csv(f"{OUTPUT_DIR}/kpi_summary.csv", index=False)
print("\n--- Core KPIs ---")
print(df_kpi)

# ---- 2. Top 10 products by orders (with category) ----
top_products_query = """
SELECT
  oi.product_id,
  COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
  COUNT(DISTINCT oi.order_id) AS total_orders,
  ROUND(SUM(oi.price), 2) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t
  ON p.product_category_name = t.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY oi.product_id
ORDER BY total_orders DESC
LIMIT 10;
"""
df_top_products = pd.read_sql_query(top_products_query, conn)
df_top_products.to_csv(f"{OUTPUT_DIR}/top_10_products.csv", index=False)
print("\n--- Top 10 Products ---")
print(df_top_products)

# ---- 3. Revenue by category (all categories, for the donut chart) ----
category_revenue_query = """
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
"""
df_category = pd.read_sql_query(category_revenue_query, conn)
df_category["pct_of_total"] = (
    100 * df_category["total_revenue"] / df_category["total_revenue"].sum()
).round(1)
df_category.to_csv(f"{OUTPUT_DIR}/revenue_by_category.csv", index=False)
print("\n--- Top 5 Categories by Revenue ---")
print(df_category.head(5))

# ---- 4. Monthly sales trend (clean window: 2017-01 to 2018-08) ----
monthly_query = """
SELECT
  strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,
  COUNT(DISTINCT o.order_id) AS total_orders,
  ROUND(SUM(oi.price), 2) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY order_month
ORDER BY order_month;
"""
df_monthly = pd.read_sql_query(monthly_query, conn)

# Drop incomplete/test-data months: 2016-09, 2016-12 (1 order each),
# and anything after 2018-08 (dataset has no delivered orders after this,
# since later orders were still in transit when this snapshot was taken)
df_monthly = df_monthly[
    (df_monthly["order_month"] >= "2017-01") & (df_monthly["order_month"] <= "2018-08")
].reset_index(drop=True)

# Month-over-month growth % (the part that's awkward in plain SQL)
df_monthly["revenue_growth_pct"] = df_monthly["total_revenue"].pct_change().mul(100).round(1)
df_monthly["orders_growth_pct"] = df_monthly["total_orders"].pct_change().mul(100).round(1)

df_monthly.to_csv(f"{OUTPUT_DIR}/monthly_trend.csv", index=False)
print("\n--- Monthly Trend (with growth %) ---")
print(df_monthly)

# ---- 5. Underperforming products (sold exactly once) ----
underperformers_query = """
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
"""
df_underperformers = pd.read_sql_query(underperformers_query, conn)
df_underperformers.to_csv(f"{OUTPUT_DIR}/underperforming_products_by_category.csv", index=False)
print("\n--- Underperforming Products by Category (top 10) ---")
print(df_underperformers.head(10))

conn.close()
print(f"\nAll CSVs exported to: {OUTPUT_DIR}")
