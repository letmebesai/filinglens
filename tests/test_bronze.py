import hashlib
import json
from datetime import datetime, timedelta, timezone

from filinglens.ingest.bronze import is_fresh, read_meta, write_raw

T0 = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)


def test_write_raw_keeps_bytes_untouched_and_writes_metadata(tmp_path):
    body = b'{"name":  "Apple Inc."}\n'
    path = write_raw(tmp_path, "CIK0000320193", body, "https://example.test/x", T0)
    assert path.read_bytes() == body
    meta = json.loads((tmp_path / "CIK0000320193.meta.json").read_text(encoding="utf-8"))
    assert meta["source_url"] == "https://example.test/x"
    assert meta["bytes"] == len(body)
    assert meta["sha256"] == hashlib.sha256(body).hexdigest()
    assert meta["retrieved_at"] == T0.isoformat()


def test_no_temp_files_left_behind(tmp_path):
    write_raw(tmp_path, "a", b"{}", "u", T0)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.json", "a.meta.json"]


def test_is_fresh_within_and_beyond_max_age(tmp_path):
    write_raw(tmp_path, "a", b"{}", "u", T0)
    day = timedelta(hours=24)
    assert is_fresh(tmp_path, "a", day, now=T0 + timedelta(hours=1))
    assert not is_fresh(tmp_path, "a", day, now=T0 + timedelta(hours=25))


def test_missing_or_corrupt_metadata_is_not_fresh(tmp_path):
    assert not is_fresh(tmp_path, "nope", timedelta(hours=24), now=T0)
    write_raw(tmp_path, "a", b"{}", "u", T0)
    (tmp_path / "a.meta.json").write_text("not json", encoding="utf-8")
    assert read_meta(tmp_path, "a") is None
    assert not is_fresh(tmp_path, "a", timedelta(hours=24), now=T0)
