DROP TABLE IF EXISTS stg_payments;
CREATE TABLE stg_payments AS
SELECT payment_id, order_id, payment_method, paid_amount_eur, payment_status
FROM Payments;
