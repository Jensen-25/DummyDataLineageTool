DROP TABLE IF EXISTS stg_order_items;
CREATE TABLE stg_order_items AS
SELECT order_item_id, order_id, product_id, quantity, unit_price_eur,
       quantity * unit_price_eur AS line_revenue
FROM OrderItems;
