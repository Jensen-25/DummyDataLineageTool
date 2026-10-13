DROP TABLE IF EXISTS stg_shipments;
CREATE TABLE stg_shipments AS
SELECT shipment_id, order_id, carrier, shipped_date, delivery_status, shipping_cost_eur
FROM Shipments;
