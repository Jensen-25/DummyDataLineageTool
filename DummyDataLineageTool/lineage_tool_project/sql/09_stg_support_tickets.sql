DROP TABLE IF EXISTS stg_support_tickets;
CREATE TABLE stg_support_tickets AS
SELECT ticket_id, customer_id, order_id, created_date, issue_type, satisfaction_score
FROM SupportTickets;
