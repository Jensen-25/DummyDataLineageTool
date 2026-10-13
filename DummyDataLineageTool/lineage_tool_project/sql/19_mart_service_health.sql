DROP TABLE IF EXISTS mart_service_health;
CREATE TABLE mart_service_health AS
SELECT s.region_name, s.issue_type,
       COUNT(s.ticket_id) AS tickets,
       ROUND(AVG(s.satisfaction_score), 2) AS avg_satisfaction,
       ROUND(SUM(f.shipping_cost_eur), 2) AS related_shipping_cost_eur
FROM int_customer_support s
JOIN int_order_finance f ON s.order_id = f.order_id
GROUP BY s.region_name, s.issue_type;
