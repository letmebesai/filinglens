"""Bronze layer: store raw SEC responses byte-for-byte, with a small metadata sidecar."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _paths(directory: Path, name: str) -> tuple[Path, Path]:
    return directory / f"{name}.json", directory / f"{name}.meta.json"


def _atomic_write(path: Path, content: bytes) -> None:
    """Write to a temp file, then rename, so a crash never leaves a half-written file."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(content)
    tmp.replace(path)


def write_raw(
    directory: Path,
    name: str,
    body: bytes,
    source_url: str,
    retrieved_at: datetime | None = None,
) -> Path:
    """Save the raw response body unchanged, plus <name>.meta.json describing where it came from."""
    directory.mkdir(parents=True, exist_ok=True)
    data_path, meta_path = _paths(directory, name)
    meta = {
        "source_url": source_url,
        "retrieved_at": (retrieved_at or utc_now()).isoformat(),
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    _atomic_write(data_path, body)
    _atomic_write(meta_path, json.dumps(meta, indent=2).encode("utf-8"))
    return data_path


def read_meta(directory: Path, name: str) -> dict | None:
    """Return the metadata for a stored file, or None if it is missing or unreadable."""
    data_path, meta_path = _paths(directory, name)
    if not data_path.exists() or not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def is_fresh(
    directory: Path,
    name: str,
    max_age: timedelta,
    now: datetime | None = None,
) -> bool:
    """True if the file exists and was retrieved less than max_age ago."""
    meta = read_meta(directory, name)
    if meta is None:
        return False
    retrieved = datetime.fromisoformat(meta["retrieved_at"])
    return ((now or utc_now()) - retrieved) < max_age
