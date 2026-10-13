DROP TABLE IF EXISTS stg_campaigns;
CREATE TABLE stg_campaigns AS
SELECT campaign_id, campaign_name, sales_channel, start_date, end_date, budget_eur
FROM Campaigns;
