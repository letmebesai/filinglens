"""Command line interface: python -m filinglens ingest"""

from __future__ import annotations

import argparse
import logging
from datetime import timedelta

from filinglens.config import DATA_DIR
from filinglens.ingest.run import run_ingest
from filinglens.sec.client import SecClient
from filinglens.sec.tickers import read_tickers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="filinglens")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest", help="Download raw SEC data into the bronze folder")
    ingest.add_argument("--tickers", default="tickers.txt", help="file with one ticker per line")
    ingest.add_argument(
        "--max-age-hours", type=float, default=24.0, help="skip files newer than this"
    )
    ingest.add_argument("--force", action="store_true", help="re-download everything")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if args.command == "ingest":
        with SecClient() as client:
            report = run_ingest(
                client,
                read_tickers(args.tickers),
                DATA_DIR / "bronze",
                timedelta(hours=args.max_age_hours),
                args.force,
            )
        print(report.summary())
        return 0 if report.ok else 1
    return 2
