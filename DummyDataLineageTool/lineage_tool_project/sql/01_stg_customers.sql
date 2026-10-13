DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers AS
SELECT customer_id, customer_name, city, country, segment
FROM Customers
WHERE is_active = 1;
