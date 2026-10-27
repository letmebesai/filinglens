import json
from pathlib import Path

from filinglens.warehouse.db import connect
from filinglens.warehouse.loaders import load_companyfacts

data = Path(r"C:\filinglens-data")
con = connect(data / "warehouse.duckdb")
total = 0
files = sorted(p for p in (data / "bronze" / "companyfacts").glob("CIK*.json") if not p.name.endswith(".meta.json"))
for f in files:
    meta = json.loads(f.with_suffix(".meta.json").read_text(encoding="utf-8"))
    total += load_companyfacts(con, f, meta["source_url"], meta["retrieved_at"], meta["sha256"])
print("files", len(files), "rows", total)
print(con.execute("SELECT count(*), count(DISTINCT cik) FROM raw_facts").fetchone())
con.close()

