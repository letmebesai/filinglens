"""Load bronze companyfacts JSON into the raw_facts table."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path

import duckdb

RAW_FACTS_COLUMNS = (
    "cik",
    "taxonomy",
    "concept",
    "unit",
    "period_start",
    "period_end",
    "value",
    "accession_number",
    "fiscal_year",
    "fiscal_period",
    "form",
    "filed_date",
    "source_url",
    "retrieved_at",
    "sha256",
)


def _rows_from_companyfacts(payload: dict, source_url: str, retrieved_at: str, sha256: str):
    cik = str(payload["cik"]).zfill(10)
    for taxonomy, concepts in payload.get("facts", {}).items():
        for concept, body in concepts.items():
            for unit, facts in body.get("units", {}).items():
                for fact in facts:
                    yield (
                        cik,
                        taxonomy,
                        concept,
                        unit,
                        fact.get("start"),
                        fact.get("end"),
                        fact.get("val"),
                        fact.get("accn"),
                        fact.get("fy"),
                        fact.get("fp"),
                        fact.get("form"),
                        fact.get("filed"),
                        source_url,
                        retrieved_at,
                        sha256,
                    )


def load_companyfacts(con: duckdb.DuckDBPyConnection, path: Path, source_url: str, retrieved_at: str, sha256: str) -> int:
    """Replace one company's raw_facts rows from a bronze file. Returns rows inserted.

    The delete, the bulk COPY and a row-count check run in one transaction, so a
    failed or short load leaves the previous rows for that CIK untouched and
    reloads never double-count.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    cik = str(payload["cik"]).zfill(10)
    cols = ", ".join(RAW_FACTS_COLUMNS)
    count = 0
    fd, tmp = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            for row in _rows_from_companyfacts(payload, source_url, retrieved_at, sha256):
                writer.writerow(row)
                count += 1
        con.execute("BEGIN")
        try:
            con.execute("DELETE FROM raw_facts WHERE cik = ?", [cik])
            if count:
                con.execute(
                    f"COPY raw_facts ({cols}) FROM '{tmp.replace(chr(92), '/')}' (FORMAT csv, HEADER false)"
                )
            loaded = con.execute("SELECT count(*) FROM raw_facts WHERE cik = ?", [cik]).fetchone()[0]
            if loaded != count:
                raise RuntimeError(f"raw_facts row count mismatch for {cik}: wrote {count}, table has {loaded}")
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    finally:
        os.remove(tmp)
    return count