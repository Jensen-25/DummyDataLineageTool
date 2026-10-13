DROP TABLE IF EXISTS stg_regions;
CREATE TABLE stg_regions AS
SELECT country, region_name, market_tier
FROM Regions;
