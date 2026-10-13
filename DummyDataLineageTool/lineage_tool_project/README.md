# Dummy SQL Data Lineage Tool

Vereist alleen **Python 3.10+** (geen pip packages).

## Starten

Open een terminal in deze projectmap en voer uit:

```bash
python3 run_pipeline.py
python3 lineage.py
open output/lineage.html  # macOS
```

`run_pipeline.py` kopieert `database/brondata.sqlite` naar `output/pipeline.sqlite` en voert automatisch alle SQL-bestanden uit op basis van hun tabelafhankelijkheden. **De bron blijft onveranderd.**

`lineage.py` analyseert de SQL-bestanden, zonder de database uit te voeren, en schrijft `output/lineage.json` en `output/lineage.html`. Klik in de HTML op een tabel om upstream/downstream relaties te zien.

## Bestanden

- `database/brondata.sqlite`: vier originele brontabellen
- `sql/01...04_*.sql`: vier staging transformaties
- `sql/05...06_*.sql`: twee verkooprapportagetabellen
- `run_pipeline.py`: centrale runner
- `lineage.py`: table-level SQL lineage parser en HTML-visualisatie
- `output/`: gegenereerde bestanden

## Semantiek

`Orders` bevat bestellingen met een status. De staging-query voor orders selecteert **alleen Completed**. `OrderItems` bevat het verkochte aantal en de historische verkoopprijs; `line_revenue = quantity * unit_price_eur`. De mart voor klantomzet neemt alleen **actieve klanten** mee. De productmart bevat ook inactieve producten als die eerder verkocht zijn.

## Parser-beperkingen

De lineage-parser gebruikt eenvoudige reguliere expressies om `CREATE TABLE ... AS SELECT`, `FROM` en `JOIN` te herkennen. Hij ondersteunt deze meegeleverde voorbeeldscripts en is bedoeld als prototype, **niet** voor complexe SQL (CTE's, subqueries, dynamische SQL, quoted identifiers, views). Voor uitgebreidere analyse kun je later overstappen op `sqlglot` met de juiste SQL-dialectinstelling.
