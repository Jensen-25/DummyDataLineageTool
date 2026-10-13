DROP TABLE IF EXISTS mart_region_performance;
CREATE TABLE mart_region_performance AS
SELECT c.region_name, c.market_tier,
       COUNT(DISTINCT l.order_id) AS orders,
       ROUND(SUM(l.line_revenue), 2) AS revenue_eur,
       ROUND(SUM(f.paid_amount_eur), 2) AS paid_eur
FROM int_customer_profile c
JOIN int_order_lines l ON c.customer_id = l.customer_id
JOIN int_order_finance f ON l.order_id = f.order_id
GROUP BY c.region_name, c.market_tier;
