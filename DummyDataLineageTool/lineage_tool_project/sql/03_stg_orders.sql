DROP TABLE IF EXISTS stg_orders;
CREATE TABLE stg_orders AS
SELECT order_id, customer_id, order_date, sales_channel
FROM Orders
WHERE status = 'Completed';
