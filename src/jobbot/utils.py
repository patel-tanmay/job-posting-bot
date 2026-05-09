from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def slugify(value: str) -> str:
    normalized = []
    for ch in value.strip().lower():
        if ch.isalnum():
            normalized.append(ch)
        else:
            normalized.append("-")
    slug = "".join(normalized)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def utc_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()

