from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class JobPosting:
    source: str
    title: str
    company: str
    location: str
    url: str
    summary: str = ""
    posted_at: Optional[str] = None
    query: str = ""
    remote_type: str = ""
    fingerprint: str = ""
    score: float = 0.0
    first_seen_at: datetime = field(default_factory=utc_now)
    sent_at: Optional[datetime] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def identity_key(self) -> str:
        base = "|".join(
            [
                self.source.strip().lower(),
                self.title.strip().lower(),
                self.company.strip().lower(),
                self.location.strip().lower(),
                self.url.strip().lower(),
            ]
        )
        return base


@dataclass(slots=True)
class QuerySpec:
    keyword: str
    location: str
    freshness_hours: int
    max_results: int = 10
    source: str = ""

    @property
    def freshness_seconds(self) -> int:
        return self.freshness_hours * 3600


@dataclass(slots=True)
class SourceSettings:
    enabled: bool = True
    freshness_hours: int = 24
    max_results: int = 10


@dataclass(slots=True)
class SearchProfile:
    name: str
    keywords: List[str]
    locations: List[str]
    sources: Dict[str, SourceSettings]
    title_exclude_terms: List[str] = field(default_factory=list)
    remote_preference: bool = False


@dataclass(slots=True)
class AppConfig:
    state_db_path: str
    telegram_message_title: str
    browser_max_pages: int = 3
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    linkedin_email: str = ""
    linkedin_password: str = ""
    browser_headless: bool = True
    browser_slow_mo_ms: int = 0
    browser_profile_dir: str = ".browser-profile"
    profiles: List[SearchProfile] = field(default_factory=list)
