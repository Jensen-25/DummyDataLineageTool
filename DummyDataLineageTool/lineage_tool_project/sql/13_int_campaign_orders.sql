DROP TABLE IF EXISTS int_campaign_orders;
CREATE TABLE int_campaign_orders AS
SELECT o.order_id, o.customer_id, o.order_date, o.sales_channel,
       c.campaign_id, c.campaign_name, c.budget_eur
FROM stg_orders o
JOIN stg_campaigns c ON o.sales_channel = c.sales_channel
                    AND o.order_date BETWEEN c.start_date AND c.end_date;
