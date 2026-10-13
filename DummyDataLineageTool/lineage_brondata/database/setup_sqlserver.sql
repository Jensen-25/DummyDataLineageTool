-- SQL Server (T-SQL). Draai dit bestand in een lege testdatabase.
-- De vier CSV-bestanden bevatten exact dezelfde brondata.
IF SCHEMA_ID('dbo') IS NULL EXEC('CREATE SCHEMA dbo');

IF OBJECT_ID('dbo.OrderItems','U') IS NOT NULL DROP TABLE dbo.OrderItems;
IF OBJECT_ID('dbo.Orders','U') IS NOT NULL DROP TABLE dbo.Orders;
IF OBJECT_ID('dbo.Products','U') IS NOT NULL DROP TABLE dbo.Products;
IF OBJECT_ID('dbo.Customers','U') IS NOT NULL DROP TABLE dbo.Customers;

CREATE TABLE dbo.Customers (
 customer_id INT PRIMARY KEY,
 customer_name NVARCHAR(100) NOT NULL,
 city NVARCHAR(60) NOT NULL,
 country CHAR(2) NOT NULL,
 segment NVARCHAR(30) NOT NULL,
 is_active BIT NOT NULL
);
CREATE TABLE dbo.Products (
 product_id INT PRIMARY KEY,
 product_name NVARCHAR(100) NOT NULL,
 category NVARCHAR(40) NOT NULL,
 unit_price_eur DECIMAL(10,2) NOT NULL CHECK (unit_price_eur >= 0),
 is_active BIT NOT NULL
);
CREATE TABLE dbo.Orders (
 order_id INT PRIMARY KEY,
 customer_id INT NOT NULL REFERENCES dbo.Customers(customer_id),
 order_date DATE NOT NULL,
 status VARCHAR(20) NOT NULL CHECK (status IN ('Completed','Cancelled','Pending')),
 sales_channel VARCHAR(30) NOT NULL
);
CREATE TABLE dbo.OrderItems (
 order_item_id INT PRIMARY KEY,
 order_id INT NOT NULL REFERENCES dbo.Orders(order_id),
 product_id INT NOT NULL REFERENCES dbo.Products(product_id),
 quantity INT NOT NULL CHECK (quantity > 0),
 unit_price_eur DECIMAL(10,2) NOT NULL CHECK (unit_price_eur >= 0)
);
-- Customers: 8 rijen
INSERT INTO dbo.Customers (customer_id, customer_name, city, country, segment, is_active) VALUES (1, N'Noordwind BV', N'Amsterdam', N'NL', N'Zakelijk', 1);
INSERT INTO dbo.Customers (customer_id, customer_name, city, country, segment, is_active) VALUES (2, N'Delta Retail', N'Rotterdam', N'NL', N'Zakelijk', 1);
INSERT INTO dbo.Customers (customer_id, customer_name, city, country, segment, is_active) VALUES (3, N'Emma de Vries', N'Utrecht', N'NL', N'Particulier', 1);
INSERT INTO dbo.Customers (customer_id, customer_name, city, country, segment, is_active) VALUES (4, N'TechHub GmbH', N'Berlin', N'DE', N'Zakelijk', 1);
INSERT INTO dbo.Customers (customer_id, customer_name, city, country, segment, is_active) VALUES (5, N'Lucas Bakker', N'Breda', N'NL', N'Particulier', 1);
INSERT INTO dbo.Customers (customer_id, customer_name, city, country, segment, is_active) VALUES (6, N'Nordic AB', N'Stockholm', N'SE', N'Zakelijk', 1);
INSERT INTO dbo.Customers (customer_id, customer_name, city, country, segment, is_active) VALUES (7, N'Oude Klant BV', N'Eindhoven', N'NL', N'Zakelijk', 0);
INSERT INTO dbo.Customers (customer_id, customer_name, city, country, segment, is_active) VALUES (8, N'Sophie Janssen', N'Haarlem', N'NL', N'Particulier', 1);

-- Products: 6 rijen
INSERT INTO dbo.Products (product_id, product_name, category, unit_price_eur, is_active) VALUES (101, N'Laptopstandaard', N'Accessoires', N'35.00', 1);
INSERT INTO dbo.Products (product_id, product_name, category, unit_price_eur, is_active) VALUES (102, N'USB-C hub', N'Elektronica', N'49.50', 1);
INSERT INTO dbo.Products (product_id, product_name, category, unit_price_eur, is_active) VALUES (103, N'Monitor 27 inch', N'Elektronica', N'219.00', 1);
INSERT INTO dbo.Products (product_id, product_name, category, unit_price_eur, is_active) VALUES (104, N'Bureaulamp', N'Kantoor', N'42.00', 1);
INSERT INTO dbo.Products (product_id, product_name, category, unit_price_eur, is_active) VALUES (105, N'Notitieboek', N'Kantoor', N'8.75', 1);
INSERT INTO dbo.Products (product_id, product_name, category, unit_price_eur, is_active) VALUES (106, N'Oud toetsenbord', N'Elektronica', N'29.00', 0);

-- Orders: 12 rijen
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1001, 1, '2026-01-05', N'Completed', N'Online');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1002, 3, '2026-01-07', N'Completed', N'Online');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1003, 2, '2026-01-12', N'Completed', N'Accountmanager');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1004, 4, '2026-02-03', N'Completed', N'Online');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1005, 1, '2026-02-10', N'Cancelled', N'Online');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1006, 5, '2026-02-14', N'Completed', N'Online');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1007, 6, '2026-03-02', N'Completed', N'Accountmanager');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1008, 8, '2026-03-11', N'Pending', N'Online');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1009, 2, '2026-03-16', N'Completed', N'Accountmanager');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1010, 3, '2026-04-04', N'Completed', N'Online');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1011, 7, '2026-04-09', N'Completed', N'Online');
INSERT INTO dbo.Orders (order_id, customer_id, order_date, status, sales_channel) VALUES (1012, 1, '2026-04-15', N'Completed', N'Online');

-- OrderItems: 23 rijen
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (1, 1001, 101, 2, N'35.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (2, 1001, 102, 1, N'49.50');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (3, 1002, 105, 3, N'8.75');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (4, 1002, 104, 1, N'42.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (5, 1003, 103, 4, N'219.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (6, 1003, 102, 2, N'49.50');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (7, 1004, 103, 1, N'219.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (8, 1004, 101, 2, N'35.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (9, 1005, 102, 3, N'49.50');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (10, 1005, 105, 2, N'8.75');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (11, 1006, 104, 1, N'42.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (12, 1006, 105, 2, N'8.75');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (13, 1007, 103, 2, N'219.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (14, 1007, 101, 3, N'35.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (15, 1008, 102, 1, N'49.50');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (16, 1008, 105, 1, N'8.75');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (17, 1009, 104, 5, N'42.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (18, 1009, 102, 2, N'49.50');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (19, 1010, 101, 1, N'35.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (20, 1010, 105, 4, N'8.75');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (21, 1011, 106, 1, N'29.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (22, 1012, 103, 1, N'219.00');
INSERT INTO dbo.OrderItems (order_item_id, order_id, product_id, quantity, unit_price_eur) VALUES (23, 1012, 104, 2, N'42.00');
