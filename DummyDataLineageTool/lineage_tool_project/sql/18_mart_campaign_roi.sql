DROP TABLE IF EXISTS mart_campaign_roi;
CREATE TABLE mart_campaign_roi AS
SELECT co.campaign_id, co.campaign_name, co.sales_channel,
       COUNT(DISTINCT co.order_id) AS attributed_orders,
       ROUND(SUM(l.line_revenue), 2) AS revenue_eur,
       MAX(co.budget_eur) AS budget_eur
FROM int_campaign_orders co
JOIN int_order_lines l ON co.order_id = l.order_id
GROUP BY co.campaign_id, co.campaign_name, co.sales_channel;
