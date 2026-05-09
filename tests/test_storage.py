from jobbot.models import JobPosting
from jobbot.storage.sqlite_store import SqliteJobStore


def test_store_tracks_seen_jobs(tmp_path):
    store = SqliteJobStore(str(tmp_path / "state.db"))
    job = JobPosting(
        source="linkedin",
        title="Data Engineer",
        company="Example",
        location="Remote",
        url="https://example.com",
        fingerprint="abc123",
    )
    assert store.has_seen("abc123") is False
    store.mark_seen([job])
    assert store.has_seen("abc123") is True

