"""Settings read from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

USER_AGENT_ENV = "FILINGLENS_SEC_USER_AGENT"

# Deliberately conservative. Check SEC's current fair-access limit in its
# EDGAR documentation and keep this comfortably below it.
MAX_REQUESTS_PER_SECOND = 5.0

DATA_DIR = Path(os.environ.get("FILINGLENS_DATA_DIR", "data"))


def get_user_agent() -> str:
    """Return the SEC User-Agent (your name and email), or fail with a clear message."""
    value = os.environ.get(USER_AGENT_ENV, "").strip()
    if not value or "@" not in value:
        raise RuntimeError(
            f"Set {USER_AGENT_ENV} to 'Your Name your.email@example.com'. "
            "SEC requires automated requests to identify who is making them."
        )
    return value
