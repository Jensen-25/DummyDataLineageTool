DROP TABLE IF EXISTS int_order_lines;
CREATE TABLE int_order_lines AS
SELECT o.order_id, o.customer_id, o.order_date, o.sales_channel,
       i.order_item_id, i.product_id, i.quantity, i.unit_price_eur, i.line_revenue
FROM stg_orders o
JOIN stg_order_items i ON o.order_id = i.order_id;
