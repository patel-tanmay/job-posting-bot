from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml
from dotenv import load_dotenv

from .models import AppConfig, SearchProfile, SourceSettings


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

def _as_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def _load_source_settings(data: Dict[str, Any]) -> Dict[str, SourceSettings]:
    sources: Dict[str, SourceSettings] = {}
    for name, source_data in data.items():
        sources[name] = SourceSettings(
            enabled=_as_bool(source_data.get("enabled"), True),
            freshness_hours=int(source_data.get("freshness_hours", 24)),
            max_results=int(source_data.get("max_results", 10)),
        )
    return sources


def load_config(path: str | os.PathLike[str]) -> AppConfig:
    load_dotenv()
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text()) or {}

    app = data.get("app", {})
    profiles_data = data.get("profiles", [])

    profiles: List[SearchProfile] = []
    for profile_data in profiles_data:
        profiles.append(
            SearchProfile(
                name=profile_data["name"],
                keywords=list(profile_data.get("keywords", [])),
                locations=list(profile_data.get("locations", [])),
                sources=_load_source_settings(profile_data.get("sources", {})),
                title_exclude_terms=list(
                    profile_data.get(
                        "title_exclude_terms",
                        ["director", "senior", "manager", "ii", "iii"],
                    )
                ),
                remote_preference=_as_bool(profile_data.get("remote_preference"), False),
            )
        )

    return AppConfig(
        state_db_path=str(app.get("state_db_path", ".jobbot/state.db")),
        telegram_message_title=str(app.get("telegram_message_title", "Morning job digest")),
        browser_max_pages=_as_int(app.get("browser_max_pages", 3), 3),
        telegram_bot_token=os.getenv("JOBBOT_TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("JOBBOT_TELEGRAM_CHAT_ID", ""),
        linkedin_email=os.getenv("JOBBOT_LINKEDIN_EMAIL", ""),
        linkedin_password=os.getenv("JOBBOT_LINKEDIN_PASSWORD", ""),
        browser_headless=_as_bool(os.getenv("JOBBOT_BROWSER_HEADLESS", "true"), True),
        browser_slow_mo_ms=_as_int(os.getenv("JOBBOT_BROWSER_SLOW_MO_MS", "0"), 0),
        browser_profile_dir=os.getenv("JOBBOT_BROWSER_PROFILE_DIR", ".browser-profile"),
        profiles=profiles,
    )
