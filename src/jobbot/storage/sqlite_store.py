from __future__ import annotations

import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

from ..models import JobPosting


class SqliteJobStore:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_jobs (
                    fingerprint TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    url TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    first_seen_at TEXT NOT NULL,
                    sent_at TEXT
                )
                """
            )
            conn.commit()

    def has_seen(self, fingerprint: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT 1 FROM seen_jobs WHERE fingerprint = ? LIMIT 1", (fingerprint,)
            )
            return cur.fetchone() is not None

    def mark_seen(self, jobs: Iterable[JobPosting]) -> None:
        with self._connect() as conn:
            for job in jobs:
                payload = repr(asdict(job))
                conn.execute(
                    """
                    INSERT OR REPLACE INTO seen_jobs
                    (fingerprint, source, title, company, location, url, payload, first_seen_at, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job.fingerprint,
                        job.source,
                        job.title,
                        job.company,
                        job.location,
                        job.url,
                        payload,
                        job.first_seen_at.isoformat(),
                        job.sent_at.isoformat() if job.sent_at else None,
                    ),
                )
            conn.commit()

