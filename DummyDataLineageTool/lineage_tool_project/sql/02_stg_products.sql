DROP TABLE IF EXISTS stg_products;
CREATE TABLE stg_products AS
SELECT product_id, product_name, category
FROM Products;
