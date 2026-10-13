# Dummy sales-brondatabase voor data lineage

## Inhoud
- `database/Customers.csv` — klantdimensie (8 klanten)
- `database/Products.csv` — productdimensie (6 producten)
- `database/Orders.csv` — orderheader / transacties (12 bestellingen)
- `database/OrderItems.csv` — orderregels (23 regels)
- `database/Regions.csv` — marktregio's per land (4 regio's)
- `database/Campaigns.csv` — marketingcampagnes per verkoopkanaal (4 campagnes)
- `database/Payments.csv` — betaalstatus en betaalmethode per order (12 betalingen)
- `database/Shipments.csv` — verzending en leverstatus per order (10 verzendingen)
- `database/SupportTickets.csv` — supportcontacten per klant/order (7 tickets)
- `database/setup_sqlserver.sql` — maakt en vult dezelfde negen tabellen als `dbo.*` in Microsoft SQL Server
- `database/brondata.sqlite` — optionele direct bruikbare SQLite-database (`main.*`, dus geen `dbo`-schema)

## Semantiek / relaties
- Customers (1) -> (N) Orders via `customer_id`
- Orders (1) -> (N) OrderItems via `order_id`
- Products (1) -> (N) OrderItems via `product_id`
- Regions (1) -> (N) Customers via `country`
- Orders (1) -> (N) Payments via `order_id`
- Orders (1) -> (N) Shipments via `order_id`
- Customers (1) -> (N) SupportTickets via `customer_id`
- Orders (1) -> (N) SupportTickets via `order_id`
- Campaigns worden gekoppeld aan Orders via `sales_channel`
- Orderbedrag = SOM(`OrderItems.quantity * OrderItems.unit_price_eur`) per order
- Alleen `Orders.status = 'Completed'` telt als gerealiseerde omzet.
- `is_active = 0` betekent historisch/inactief, niet verwijderen.
- Alle `unit_price_eur` bedragen zijn fictieve EUR-bedragen exclusief btw.
- De prijs in OrderItems is de prijs op de besteldatum (kan afwijken van huidige productcatalogusprijs).
- Sales_channel geeft het bestelkanaal.

## Gebruik
**SQL Server:** voer `setup_sqlserver.sql` uit in een wegwerp/testdatabase. Script dropt bestaande tabellen met deze namen en maakt ze opnieuw aan.

**SQLite:** open `brondata.sqlite` en query bijvoorbeeld `SELECT * FROM Orders;`.

**CSV:** laad de losse CSV-bestanden in je eigen database of pipeline.

## Interessante lineage-voorbeelden
1. `Customers + Regions -> int_customer_profile -> meerdere marts`
2. `Orders + OrderItems -> int_order_lines -> product, klant, regio en campagne marts`
3. `Orders + Payments + Shipments -> int_order_finance -> omzet en service health`
4. `SupportTickets + int_customer_profile + int_order_finance -> mart_service_health`
5. `Campaigns + Orders + OrderItems -> mart_campaign_roi`
