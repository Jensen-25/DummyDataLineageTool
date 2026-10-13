DROP TABLE IF EXISTS int_customer_profile;
CREATE TABLE int_customer_profile AS
SELECT c.customer_id, c.customer_name, c.city, c.country, c.segment,
       r.region_name, r.market_tier
FROM stg_customers c
JOIN stg_regions r ON c.country = r.country;
