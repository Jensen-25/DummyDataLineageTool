# Dummy sales-brondatabase voor data lineage

## Inhoud
- `database/Customers.csv` — klantdimensie (8 klanten)
- `database/Products.csv` — productdimensie (6 producten)
- `database/Orders.csv` — orderheader / transacties (12 bestellingen)
- `database/OrderItems.csv` — orderregels (23 regels)
- `database/setup_sqlserver.sql` — maakt en vult dezelfde vier tabellen als `dbo.*` in Microsoft SQL Server
- `database/brondata.sqlite` — optionele direct bruikbare SQLite-database (`main.*`, dus geen `dbo`-schema)

## Semantiek / relaties
- Customers (1) -> (N) Orders via `customer_id`
- Orders (1) -> (N) OrderItems via `order_id`
- Products (1) -> (N) OrderItems via `product_id`
- Orderbedrag = SOM(`OrderItems.quantity * OrderItems.unit_price_eur`) per order
- Alleen `Orders.status = 'Completed'` telt als gerealiseerde omzet.
- `is_active = 0` betekent historisch/inactief, niet verwijderen.
- Alle `unit_price_eur` bedragen zijn fictieve EUR-bedragen exclusief btw.
- De prijs in OrderItems is de prijs op de besteldatum (kan afwijken van huidige productcatalogusprijs).
- Sales_channel geeft het bestelkanaal.

## Gebruik
**SQL Server:** voer `setup_sqlserver.sql` uit in een wegwerp/testdatabase. Script dropt bestaande tabellen met deze namen (OrderItems, Orders, Products, Customers) en maakt ze opnieuw aan.

**SQLite:** open `brondata.sqlite` en query bijvoorbeeld `SELECT * FROM Orders;`.

**CSV:** laad de vier losse CSV-bestanden in je eigen database of pipeline.

## Interessante lineage-voorbeelden
1. `dbo.Customers -> stg_customers -> mart_customer_sales`
2. `dbo.Orders + dbo.OrderItems -> stg_order_lines -> mart_monthly_revenue`
3. `dbo.Products + dbo.OrderItems -> mart_product_revenue`
4. `dbo.Orders.status` beïnvloedt welke orders worden meegeteld in omzetberekeningen.
