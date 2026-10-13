DROP TABLE IF EXISTS mart_customer_revenue;
CREATE TABLE mart_customer_revenue AS
SELECT c.customer_id, c.customer_name, c.segment, c.region_name,
       COUNT(DISTINCT l.order_id) AS order_count,
       ROUND(SUM(l.line_revenue), 2) AS revenue_eur,
       ROUND(SUM(f.shipping_cost_eur), 2) AS shipping_cost_eur
FROM int_customer_profile c
JOIN int_order_lines l ON c.customer_id = l.customer_id
JOIN int_order_finance f ON l.order_id = f.order_id
GROUP BY c.customer_id, c.customer_name, c.segment, c.region_name;
