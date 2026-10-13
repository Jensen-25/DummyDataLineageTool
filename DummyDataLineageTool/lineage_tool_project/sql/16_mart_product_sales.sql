DROP TABLE IF EXISTS mart_product_sales;
CREATE TABLE mart_product_sales AS
SELECT p.product_id, p.product_name, p.category,
       SUM(l.quantity) AS units_sold,
       ROUND(SUM(l.line_revenue), 2) AS revenue_eur
FROM stg_products p
JOIN int_order_lines l ON p.product_id = l.product_id
GROUP BY p.product_id, p.product_name, p.category;
