# Environment variables

FilingLens reads configuration from environment variables only. There is no `.env` loader, so setting these in your shell is required.

| Variable | Required | Purpose |
|---|---|---|
| `FILINGLENS_SEC_USER_AGENT` | Yes | Identifies you to SEC EDGAR on every request. Use your name and a real contact email. |
| `FILINGLENS_DATA_DIR` | Strongly recommended | Root folder for bronze files and the DuckDB warehouse. If unset, it falls back to a relative `data` folder in the current directory. |

## Windows (PowerShell)

Set these in every new terminal:

    $env:FILINGLENS_DATA_DIR = "C:\filinglens-data"
    $env:FILINGLENS_SEC_USER_AGENT = "Your Name your@email.com"

## macOS / Linux

    export FILINGLENS_DATA_DIR="$HOME/filinglens-data"
    export FILINGLENS_SEC_USER_AGENT="Your Name your@email.com"

## Notes

- The client's request rate is capped by `MAX_REQUESTS_PER_SECOND` in `src/filinglens/config.py`.
- A missing `FILINGLENS_DATA_DIR` fails silently by writing to a different folder, so check it before running ingest or load.
