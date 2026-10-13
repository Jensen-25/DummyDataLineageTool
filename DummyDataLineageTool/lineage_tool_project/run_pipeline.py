"""Run SQL models against a COPY of the supplied SQLite source database."""
import shutil
import sqlite3
from pathlib import Path

from lineage import ROOT, SQL_DIR, OUT_DIR, execution_order, get_lineage, write_html

SOURCE = ROOT / "database" / "brondata.sqlite"
DESTINATION = OUT_DIR / "pipeline.sqlite"


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Source database not found: {SOURCE}")
    scripts = execution_order(get_lineage(SQL_DIR))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, DESTINATION)
    with sqlite3.connect(DESTINATION) as conn:
        for script in scripts:
            query = (SQL_DIR / script["script"]).read_text(encoding="utf-8")
            conn.executescript(query)
            count = conn.execute(f'SELECT COUNT(*) FROM "{script["target"]}"').fetchone()[0]
            print(f'{script["script"]} -> {script["target"]}: {count} rows')
    write_html(scripts, OUT_DIR / "lineage.html")
    print(f"\nOutput database: {DESTINATION}")
    print(f"Lineage diagram: {OUT_DIR / 'lineage.html'}")


if __name__ == "__main__":
    main()
