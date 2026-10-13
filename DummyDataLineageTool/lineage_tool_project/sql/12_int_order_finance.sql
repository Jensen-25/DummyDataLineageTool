DROP TABLE IF EXISTS int_order_finance;
CREATE TABLE int_order_finance AS
SELECT o.order_id, o.customer_id, o.order_date, o.sales_channel,
       p.payment_method, p.payment_status, p.paid_amount_eur,
       s.carrier, s.delivery_status, s.shipping_cost_eur
FROM stg_orders o
JOIN stg_payments p ON o.order_id = p.order_id
JOIN stg_shipments s ON o.order_id = s.order_id;
