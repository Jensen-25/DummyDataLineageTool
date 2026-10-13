DROP TABLE IF EXISTS int_customer_support;
CREATE TABLE int_customer_support AS
SELECT p.customer_id, p.customer_name, p.segment, p.region_name,
       t.ticket_id, t.order_id, t.issue_type, t.satisfaction_score
FROM int_customer_profile p
JOIN stg_support_tickets t ON p.customer_id = t.customer_id;
