"""Minimal table-level SQL lineage. Supports CREATE TABLE ... AS SELECT + FROM/JOIN.

This regex-based parser is intended for the included dummy SQL scripts; it is NOT
an arbitrary SQL parser. For production SQL use a dialect-aware parser (SQLGlot).
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

# Constants declared at the module level for easier testing 
ROOT = Path(__file__).resolve().parent
SQL_DIR = ROOT / "sql"
OUT_DIR = ROOT / "output"
IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
TABLE_PATTERN = rf"{IDENT}(?:\.{IDENT})?"

# Regexes for parsing SQL scripts

# regex 
CREATE_RE = re.compile(rf"\bCREATE\s+TABLE\s+({TABLE_PATTERN})\s+AS\s+SELECT\b", re.I)
READ_RE = re.compile(rf"\b(?:FROM|JOIN)\s+({TABLE_PATTERN})\b", re.I)
SOURCE_RE = re.compile(
    rf"\b(FROM|JOIN)\s+({TABLE_PATTERN})(?:\s+(?:AS\s+)?"
    rf"(?!(?:ON|WHERE|JOIN|GROUP|ORDER|HAVING|LIMIT)\b)({IDENT}))?",
    re.I,
)

# join rule for the regex parser, capturing the join condition and any alias used for the table.
JOIN_RE = re.compile(
    rf"\bJOIN\s+({TABLE_PATTERN})(?:\s+(?:AS\s+)?"
    rf"(?!(?:ON|WHERE|JOIN|GROUP|ORDER|HAVING|LIMIT)\b)({IDENT}))?"
    rf"\s+ON\s+(.*?)(?=\bJOIN\b|\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bHAVING\b|;|$)",
    re.I | re.S,
)
# Regex for removing comments from SQL scripts
COMMENT_RE = re.compile(r"/\*.*?\*/|--[^\n]*", re.S)

# Reserved words that cannot be used as table aliases, since 
# these would be interpreted as SQL keywords.
RESERVED_WORDS = {"ON", "WHERE", "JOIN", "GROUP", "ORDER", "HAVING", "LIMIT"}


def get_lineage(sql_dir: Path = SQL_DIR) -> list[dict]:
    """
    Get the lineage of all SQL scripts in the specified directory.
    """
    scripts = []

    # Parse the SQL scripts and extract target tables.
    for path in sorted(sql_dir.glob("*.sql")):
        sql = COMMENT_RE.sub("", path.read_text(encoding="utf-8"))
        match = CREATE_RE.search(sql)

    # Validation whether the script creates at least one table 
        if not match:
            raise ValueError(f"No CREATE TABLE ... AS SELECT found in {path.name}")
        target = match.group(1)
        sources = list(dict.fromkeys(READ_RE.findall(sql)))

        if not sources:
            raise ValueError(f"No FROM or JOIN source found in {path.name}")

        # 
        scripts.append({
            "script": path.name,
            "target": target,
            "sources": sources,
            "source_keys": get_source_keys(sql),
        })

    if not scripts:
        raise ValueError(f"No .sql files found in {sql_dir}")
    
    targets = [entry["target"].lower() for entry in scripts]

    # Validation whether multiple scripts create the same target table.
    if len(set(targets)) != len(targets):
        raise ValueError("Multiple SQL scripts create the same target table")
    add_dependencies(scripts)
    return scripts


def get_source_keys(sql: str) -> list[dict]:
    """
    Extract direct source tables with the JOIN key/condition used.
    """
    # Collect the source tables and initialize 
    sources = list(dict.fromkeys(READ_RE.findall(sql)))
    source_keys = {source.lower(): [] for source in sources}
    aliases = {}

    for match in SOURCE_RE.finditer(sql):
        keyword, table, alias = match.groups()
        alias = alias if alias and alias.upper() not in RESERVED_WORDS else table.split(".")[-1]
        aliases[alias.lower()] = table
        aliases[table.lower()] = table

    for match in JOIN_RE.finditer(sql):
        table, alias, condition = match.groups()
        alias = alias if alias and alias.upper() not in RESERVED_WORDS else table.split(".")[-1]
        condition = clean_condition(condition)
        referenced_sources = {
            aliases[name.lower()].lower()
            for name in re.findall(rf"\b({IDENT})\.", condition)
            if name.lower() in aliases
        }
        referenced_sources.add(table.lower())
        for source in referenced_sources:
            if source in source_keys and condition not in source_keys[source]:
                source_keys[source].append(condition)

    return [
        {"source": source, "key": "; ".join(source_keys[source.lower()]) or None}
        for source in sources
    ]


def clean_condition(condition: str) -> str:
    return " ".join(condition.strip().rstrip(";").split())


def add_dependencies(scripts: list[dict]) -> None:
    """Add direct SQL script dependencies based on source tables."""
    producers = {entry["target"].lower(): entry["script"] for entry in scripts}
    for entry in scripts:
        entry["dependencies"] = [
            producers[source.lower()]
            for source in entry["sources"]
            if source.lower() in producers
        ]
        entry["dependency_keys"] = [
            {
                "source": source_key["source"],
                "script": producers[source_key["source"].lower()],
                "key": source_key["key"],
            }
            for source_key in entry["source_keys"]
            if source_key["source"].lower() in producers
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
        if name not in targets:
            kind = "source"
        elif name.startswith("mart_"):
            kind = "mart"
        elif name.startswith("int_"):
            kind = "intermediate"
        else:
            kind = "stage"
        svg.append(f'<g class="node {kind}" data-name="{html.escape(name)}" tabindex="0" role="button"><rect x="{x-100}" y="{y-25}" width="200" height="50" rx="9"/><text x="{x}" y="{y+5}" text-anchor="middle">{html.escape(name)}</text></g>')
    data = json.dumps(scripts).replace("<", "\\u003c")
    document = """<!doctype html><html lang="nl"><meta charset="utf-8"><title>SQL Data Lineage</title>
<style>body{font:15px system-ui,sans-serif;margin:0;background:#f5f7fb;color:#172437}header{padding:24px 36px;background:white;border-bottom:1px solid #dde3eb}h1{margin:0 0 6px;font-size:28px}p{margin:6px 0;color:#536278}.layout{display:flex;gap:20px;padding:24px;align-items:flex-start}.graph{background:white;border:1px solid #dbe3ed;border-radius:10px;overflow:auto;flex:1;box-shadow:0 12px 28px rgba(31,45,61,.06)}aside{width:390px;background:white;border:1px solid #dbe3ed;border-radius:10px;padding:22px;position:sticky;top:20px;box-shadow:0 12px 28px rgba(31,45,61,.07)}aside h2{font-size:21px;margin:0 0 15px;color:#132033;overflow-wrap:anywhere}.node{cursor:pointer}.node rect{stroke-width:1.4}.node.source rect{fill:#eef1f5;stroke:#7d8998}.node.stage rect{fill:#d8ecff;stroke:#357fbd}.node.intermediate rect{fill:#efe1ff;stroke:#8b5cc7}.node.mart rect{fill:#daf4e4;stroke:#34966c}.node text{fill:#1b2b42;font:13px system-ui,sans-serif}.node.active rect{stroke:#df7f21;stroke-width:3}.node.faded,.edge.faded{opacity:.16}.edge{fill:none;stroke:#7189a4;stroke-width:2.1}.muted{color:#697789}.legend{margin:0 0 18px;padding:12px 0 14px;list-style:none;border-top:1px solid #edf1f6;border-bottom:1px solid #edf1f6}.legend li{display:flex;align-items:center;gap:10px;margin:8px 0;color:#44536a;font-weight:650}.swatch{width:15px;height:15px;border-radius:4px;border:1px solid;flex:0 0 auto}.swatch.source{background:#eef1f5;border-color:#7d8998}.swatch.stage{background:#d8ecff;border-color:#357fbd}.swatch.intermediate{background:#efe1ff;border-color:#8b5cc7}.swatch.mart{background:#daf4e4;border-color:#34966c}.section{margin:16px 0}.section-title{font-size:18px;font-weight:800;color:#26354a;margin:0 0 8px}.script-badge{display:block;width:max-content;max-width:100%;box-sizing:border-box;padding:8px 10px;border-radius:7px;background:#eaf1f8;color:#26354a;font-size:16px;font-weight:800;overflow-wrap:anywhere}.relation{padding:10px 11px;margin:8px 0;border:1px solid #e0e7f0;border-radius:8px;background:#fbfcfe}.relation-source{display:block;color:#19283d;font-size:16px;font-weight:800;overflow-wrap:anywhere}.relation-script{display:block;margin-top:4px;color:#526176;font-size:14px;font-weight:700;overflow-wrap:anywhere}.relation-key{display:block;margin-top:5px;color:#65748a;font:13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;line-height:1.35;overflow-wrap:anywhere}.tag{display:inline-block;margin:3px 3px 3px 0;padding:5px 8px;border-radius:6px;background:#eef2f7;color:#526176;font-size:13px;font-weight:650}button{padding:8px 12px;border:1px solid #cbd5df;border-radius:7px;background:white;cursor:pointer;font-weight:650}@media(max-width:900px){.layout{display:block}aside{width:auto;position:static;margin-top:14px}}</style>
<header><h1>SQL Data Lineage</h1><p>Klik op een tabel om de upstream-bronnen en downstream-afhankelijkheden te zien.</p></header><div class="layout"><div class="graph"><svg id="graph" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 __WIDTH__ __HEIGHT__" style="min-width:900px;width:100%">__SVG__</svg></div><aside><h2 id="selected">Selecteer een tabel</h2><ul class="legend"><li><span class="swatch source"></span>Brondata</li><li><span class="swatch stage"></span>Staging</li><li><span class="swatch intermediate"></span>Intermediate</li><li><span class="swatch mart"></span>Mart / eindtabel</li></ul><div id="details" class="muted">Klik op een node voor script, dependencies en relaties.</div><p><button onclick="reset()">Reset selectie</button></p></aside></div>
<script>const scripts=__DATA__;const edges=scripts.flatMap(s=>s.sources.map(src=>[src,s.target]));function reachable(start,reverse=false){let seen=new Set(),queue=[start];while(queue.length){let n=queue.shift();for(let [a,b] of edges){let from=reverse?b:a,to=reverse?a:b;if(from===n&&!seen.has(to)){seen.add(to);queue.push(to)}}}return seen}function choose(name){let up=reachable(name,true),down=reachable(name),included=new Set([name,...up,...down]);document.querySelectorAll('.node').forEach(n=>{n.classList.toggle('faded',!included.has(n.dataset.name));n.classList.toggle('active',n.dataset.name===name)});document.querySelectorAll('.edge').forEach(e=>e.classList.toggle('faded',!(included.has(e.dataset.src)&&included.has(e.dataset.dst))));let s=scripts.find(s=>s.target===name);document.getElementById('selected').textContent=name;let fmt=names=>names.length?names.sort().map(n=>'<span class="tag">'+escapeHtml(n)+'</span>').join(''):'<span class="muted">Geen</span>';let section=(title,body)=>'<div class="section"><div class="section-title">'+escapeHtml(title)+'</div>'+body+'</div>';let fmtRelations=items=>items&&items.length?items.map(i=>'<div class="relation"><span class="relation-source">'+escapeHtml(i.source)+'</span>'+(i.script?'<span class="relation-script">'+escapeHtml(i.script)+'</span>':'')+'<span class="relation-key">'+escapeHtml(i.key||'geen join-key / directe bron')+'</span></div>').join(''):'<span class="muted">Geen</span>';let html=s?section('SQL script','<span class="script-badge">'+escapeHtml(s.script)+'</span>')+section('Dependencies',fmtRelations(s.dependency_keys))+section('Directe input-tabellen',fmt(s.sources))+section('Input keys',fmtRelations(s.source_keys))+section('Upstream-tabellen',fmt([...up]))+section('Downstream-tabellen',fmt([...down])):section('SQL script','<span class="script-badge">Brontabel</span>')+section('Dependencies','<span class="muted">Geen</span>')+section('Downstream-tabellen',fmt([...down]));document.getElementById('details').innerHTML=html}function escapeHtml(s){return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}function reset(){document.querySelectorAll('.node,.edge').forEach(n=>n.classList.remove('faded','active'));document.getElementById('selected').textContent='Selecteer een tabel';document.getElementById('details').textContent='Klik op een node voor script, dependencies en relaties.'}document.querySelectorAll('.node').forEach(n=>{n.addEventListener('click',()=>choose(n.dataset.name));n.addEventListener('keydown',e=>{if(e.key==='Enter')choose(n.dataset.name)})});</script></html>"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document.replace("__WIDTH__", str(width)).replace("__HEIGHT__", str(height)).replace("__SVG__", "\n".join(svg)).replace("__DATA__", data), encoding="utf-8")


def main() -> None:
    scripts = get_lineage()
    for s in execution_order(scripts):
        dependencies = ", ".join(s["dependencies"]) or "geen SQL-script dependencies"
        keys = "; ".join(
            f'{item["source"]}: {item["key"] or "geen join-key"}'
            for item in s["source_keys"]
        )
        print(f'{s["script"]}: {", ".join(s["sources"])} -> {s["target"]} | dependencies: {dependencies} | keys: {keys}')
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "lineage.json").write_text(json.dumps(scripts, indent=2), encoding="utf-8")
    write_html(scripts, OUT_DIR / "lineage.html")
    print(f"\nOpen {OUT_DIR / 'lineage.html'} in je browser")


if __name__ == "__main__":
    main()
