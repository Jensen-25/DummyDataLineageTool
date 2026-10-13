DROP TABLE IF EXISTS mart_product_sales;
CREATE TABLE mart_product_sales AS
SELECT p.product_id, p.product_name, p.category,
       SUM(i.quantity) AS units_sold,
       ROUND(SUM(i.line_revenue), 2) AS revenue_eur
FROM stg_products p
JOIN stg_order_items i ON p.product_id = i.product_id
JOIN stg_orders o ON i.order_id = o.order_id
GROUP BY p.product_id, p.product_name, p.category;
