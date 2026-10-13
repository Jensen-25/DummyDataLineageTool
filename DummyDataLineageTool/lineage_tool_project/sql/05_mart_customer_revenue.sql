DROP TABLE IF EXISTS mart_customer_revenue;
CREATE TABLE mart_customer_revenue AS
SELECT c.customer_id, c.customer_name, c.segment,
       COUNT(DISTINCT o.order_id) AS order_count,
       ROUND(SUM(i.line_revenue), 2) AS revenue_eur
FROM stg_customers c
JOIN stg_orders o ON c.customer_id = o.customer_id
JOIN stg_order_items i ON o.order_id = i.order_id
GROUP BY c.customer_id, c.customer_name, c.segment;
