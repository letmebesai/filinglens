"""Load bronze companyfacts JSON into the raw_facts table."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path

import duckdb


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
                        fact.get("end"),
                        fact.get("val"),
                        fact.get("accn"),
                        fact.get("filed"),
                        source_url,
                        retrieved_at,
                        sha256,
                    )


def load_companyfacts(con: duckdb.DuckDBPyConnection, path: Path, source_url: str, retrieved_at: str, sha256: str) -> int:
    """Insert one companyfacts file via bulk COPY. Returns the number of rows inserted."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    count = 0
    fd, tmp = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            for row in _rows_from_companyfacts(payload, source_url, retrieved_at, sha256):
                writer.writerow(row)
                count += 1
        if count:
            con.execute(f"COPY raw_facts FROM '{tmp.replace(chr(92), '/')}' (FORMAT csv)")
    finally:
        os.remove(tmp)
    return count