"""Download raw SEC data for a list of tickers into the bronze folder."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

from filinglens.ingest.bronze import is_fresh, write_raw
from filinglens.sec.client import DATA_BASE, WWW_BASE, SecClient, SecError
from filinglens.sec.tickers import build_cik_map, resolve

log = logging.getLogger(__name__)

TICKERS_URL = f"{WWW_BASE}/files/company_tickers.json"

# One folder per kind of data under data/bronze/.
SOURCES = {
    "submissions": DATA_BASE + "/submissions/CIK{cik}.json",
    "companyfacts": DATA_BASE + "/api/xbrl/companyfacts/CIK{cik}.json",
}


@dataclass
class IngestReport:
    fetched: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)
    missing_tickers: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failed and not self.missing_tickers

    def summary(self) -> str:
        lines = [
            f"fetched: {len(self.fetched)}",
            f"skipped (already fresh): {len(self.skipped)}",
            f"failed: {len(self.failed)}",
        ]
        for label, reason in self.failed.items():
            lines.append(f"  FAILED {label}: {reason}")
        if self.missing_tickers:
            lines.append(f"tickers not found at SEC: {', '.join(self.missing_tickers)}")
        return "\n".join(lines)


def _load_ticker_map(client: SecClient, bronze_dir: Path, max_age: timedelta, force: bool):
    """Get SEC's ticker list (from bronze if fresh, else download) as {ticker: cik}."""
    directory = bronze_dir / "reference"
    path = directory / "company_tickers.json"
    if not force and is_fresh(directory, "company_tickers", max_age):
        return build_cik_map(json.loads(path.read_text(encoding="utf-8")))
    response = client.get(TICKERS_URL)
    write_raw(directory, "company_tickers", response.content, str(response.url))
    return build_cik_map(response.json())


def run_ingest(
    client: SecClient,
    tickers: list[str],
    bronze_dir: Path,
    max_age: timedelta = timedelta(hours=24),
    force: bool = False,
) -> IngestReport:
    """Fetch submissions and company facts for each ticker. Safe to re-run."""
    report = IngestReport()
    cik_map = _load_ticker_map(client, bronze_dir, max_age, force)
    found, report.missing_tickers = resolve(tickers, cik_map)

    for ticker, cik in found.items():
        name = f"CIK{cik}"
        for kind, template in SOURCES.items():
            label = f"{ticker}/{kind}"
            directory = bronze_dir / kind
            if not force and is_fresh(directory, name, max_age):
                report.skipped.append(label)
                continue
            try:
                response = client.get(template.format(cik=cik))
            except SecError as exc:
                log.warning("failed %s: %s", label, exc)
                report.failed[label] = str(exc)
                continue
            write_raw(directory, name, response.content, str(response.url))
            report.fetched.append(label)
            log.info("fetched %s", label)
    return report

