"""Minimal table-level SQL lineage. Supports CREATE TABLE ... AS SELECT + FROM/JOIN.

This regex-based parser is intended for the included dummy SQL scripts; it is NOT
an arbitrary SQL parser. For production SQL use a dialect-aware parser (SQLGlot).
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "output"
IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
TABLE_PATTERN = rf"{IDENT}(?:\.{IDENT})?"
CREATE_RE = re.compile(rf"\bCREATE\s+TABLE\s+({TABLE_PATTERN})\s+AS\s+SELECT\b", re.I)
READ_RE = re.compile(rf"\b(?:FROM|JOIN)\s+({TABLE_PATTERN})\b", re.I)
COMMENT_RE = re.compile(r"/\*.*?\*/|--[^\n]*", re.S)


def get_lineage(sql_dir: Path = SQL_DIR) -> list[dict]:
    scripts = []
    for path in sorted(sql_dir.glob("*.sql")):
        sql = COMMENT_RE.sub("", path.read_text(encoding="utf-8"))
        match = CREATE_RE.search(sql)
        if not match:
            raise ValueError(f"No CREATE TABLE ... AS SELECT found in {path.name}")
        target = match.group(1)
        sources = list(dict.fromkeys(READ_RE.findall(sql)))
        if not sources:
            raise ValueError(f"No FROM or JOIN source found in {path.name}")
        scripts.append({"script": path.name, "target": target, "sources": sources})
    if not scripts:
        raise ValueError(f"No .sql files found in {sql_dir}")
    targets = [entry["target"].lower() for entry in scripts]
    if len(set(targets)) != len(targets):
        raise ValueError("Multiple SQL scripts create the same target table")
    add_dependencies(scripts)
    return scripts


def add_dependencies(scripts: list[dict]) -> None:
    """Add direct SQL script dependencies based on source tables."""
    producers = {entry["target"].lower(): entry["script"] for entry in scripts}
    for entry in scripts:
        entry["dependencies"] = [
            producers[source.lower()]
            for source in entry["sources"]
            if source.lower() in producers
        ]


def execution_order(scripts: list[dict]) -> list[dict]:
    """Topological ordering, with actionable error for circular dependencies."""
    producers = {s["target"].lower(): s for s in scripts}
    pending = scripts.copy()
    result = []
    complete = set()
    while pending:
        ready = [s for s in pending if all(
            src.lower() not in producers or src.lower() in complete
            for src in s["sources"]
        )]
        if not ready:
            raise ValueError("Circular dependency between SQL scripts")
        for s in ready:
            result.append(s)
            complete.add(s["target"].lower())
            pending.remove(s)
    return result


def write_html(scripts: list[dict], destination: Path) -> None:
    targets = {s["target"] for s in scripts}
    nodes = sorted(set(targets).union(*(set(s["sources"]) for s in scripts)))
    levels = {}
    for s in execution_order(scripts):
        for src in s["sources"]:
            levels.setdefault(src, 0)
        levels[s["target"]] = 1 + max(levels[src] for src in s["sources"])
    layers = {}
    for node in nodes:
        layers.setdefault(levels[node], []).append(node)
    positions = {}
    for level, names in layers.items():
        for index, name in enumerate(names):
            positions[name] = (140 + level * 300, 85 + index * 105)
    height = max(390, 170 + 105 * max(len(x) for x in layers.values()))
    width = max(900, 310 + 300 * max(layers))
    svg = []
    for s in scripts:
        for src in s["sources"]:
            x1, y1 = positions[src]
            x2, y2 = positions[s["target"]]
            svg.append(f'<path class="edge" data-src="{html.escape(src)}" data-dst="{html.escape(s["target"])}" d="M{x1+100},{y1} C{x1+180},{y1} {x2-180},{y2} {x2-100},{y2}"/>')
    for name in nodes:
        x, y = positions[name]
        kind = "source" if name not in targets else "mart" if name.startswith("mart_") else "stage"
        svg.append(f'<g class="node {kind}" data-name="{html.escape(name)}" tabindex="0" role="button"><rect x="{x-100}" y="{y-25}" width="200" height="50" rx="9"/><text x="{x}" y="{y+5}" text-anchor="middle">{html.escape(name)}</text></g>')
    data = json.dumps(scripts).replace("<", "\\u003c")
    document = """<!doctype html><html lang="nl"><meta charset="utf-8"><title>SQL Data Lineage</title>
<style>body{font:15px system-ui,sans-serif;margin:0;background:#f6f8fb;color:#172437}header{padding:22px 32px;background:white;border-bottom:1px solid #dde3eb}h1{margin:0 0 6px}p{margin:5px 0;color:#536278}.layout{display:flex;gap:18px;padding:22px;align-items:flex-start}.graph{background:white;border:1px solid #dde3eb;border-radius:12px;overflow:auto;flex:1}aside{width:275px;background:white;border:1px solid #dde3eb;border-radius:12px;padding:20px;position:sticky;top:20px}aside h2{font-size:18px;margin:0 0 13px}.node{cursor:pointer}.node rect{stroke-width:1.4}.node.source rect{fill:#e5eaf0;stroke:#8492a6}.node.stage rect{fill:#d9ebff;stroke:#4d8ac1}.node.mart rect{fill:#d9f4e8;stroke:#3f9b77}.node text{fill:#1b2b42;font:13px system-ui,sans-serif}.node.active rect{stroke:#e08724;stroke-width:3}.node.faded,.edge.faded{opacity:.16}.edge{fill:none;stroke:#7189a4;stroke-width:2.1}.muted{color:#697789}.tag{display:inline-block;margin:3px 2px;padding:4px 7px;border-radius:5px;background:#eef2f7;font-size:12px}button{padding:7px 11px;border:1px solid #cbd5df;border-radius:7px;background:white;cursor:pointer}@media(max-width:800px){.layout{display:block}aside{width:auto;position:static;margin-top:12px}}</style>
<header><h1>SQL Data Lineage</h1><p>Klik op een tabel om de upstream-bronnen en downstream-afhankelijkheden te zien.</p></header><div class="layout"><div class="graph"><svg id="graph" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 __WIDTH__ __HEIGHT__" style="min-width:800px;width:100%">__SVG__</svg></div><aside><h2 id="selected">Selecteer een tabel</h2><div id="details" class="muted">Grijs = bron; blauw = staging; groen = eindtabel.</div><p><button onclick="reset()">Reset selectie</button></p></aside></div>
<script>const scripts=__DATA__;const edges=scripts.flatMap(s=>s.sources.map(src=>[src,s.target]));function reachable(start,reverse=false){let seen=new Set(),queue=[start];while(queue.length){let n=queue.shift();for(let [a,b] of edges){let from=reverse?b:a,to=reverse?a:b;if(from===n&&!seen.has(to)){seen.add(to);queue.push(to)}}}return seen}function choose(name){let up=reachable(name,true),down=reachable(name),included=new Set([name,...up,...down]);document.querySelectorAll('.node').forEach(n=>{n.classList.toggle('faded',!included.has(n.dataset.name));n.classList.toggle('active',n.dataset.name===name)});document.querySelectorAll('.edge').forEach(e=>e.classList.toggle('faded',!(included.has(e.dataset.src)&&included.has(e.dataset.dst))));let s=scripts.find(s=>s.target===name);document.getElementById('selected').textContent=name;let fmt=names=>names.length?names.sort().map(n=>'<span class="tag">'+escapeHtml(n)+'</span>').join(''):'Geen';document.getElementById('details').innerHTML='<p><b>SQL script:</b><br>'+(s?'<span class="tag">'+escapeHtml(s.script)+'</span>':'Brontabel')+'</p><p><b>Dependencies:</b><br>'+fmt(s?s.dependencies:[])+'</p><p><b>Directe input-tabellen:</b><br>'+fmt(s?s.sources:[])+'</p><p><b>Upstream-tabellen:</b><br>'+fmt([...up])+'</p><p><b>Downstream-tabellen:</b><br>'+fmt([...down])+'</p>'}function escapeHtml(s){return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function reset(){document.querySelectorAll('.node,.edge').forEach(n=>n.classList.remove('faded','active'));document.getElementById('selected').textContent='Selecteer een tabel';document.getElementById('details').textContent='Grijs = bron; blauw = staging; groen = eindtabel.'}document.querySelectorAll('.node').forEach(n=>{n.addEventListener('click',()=>choose(n.dataset.name));n.addEventListener('keydown',e=>{if(e.key==='Enter')choose(n.dataset.name)})});</script></html>"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document.replace("__WIDTH__", str(width)).replace("__HEIGHT__", str(height)).replace("__SVG__", "\n".join(svg)).replace("__DATA__", data), encoding="utf-8")


def main() -> None:
    scripts = get_lineage()
    for s in execution_order(scripts):
        dependencies = ", ".join(s["dependencies"]) or "geen SQL-script dependencies"
        print(f'{s["script"]}: {", ".join(s["sources"])} -> {s["target"]} | dependencies: {dependencies}')
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "lineage.json").write_text(json.dumps(scripts, indent=2), encoding="utf-8")
    write_html(scripts, OUT_DIR / "lineage.html")
    print(f"\nOpen {OUT_DIR / 'lineage.html'} in je browser")


if __name__ == "__main__":
    main()
