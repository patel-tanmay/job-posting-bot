from __future__ import annotations

from urllib.parse import quote_plus

from .models import QuerySpec


def build_linkedin_url(query: QuerySpec, page: int = 1) -> str:
    keyword = quote_plus(query.keyword)
    location = quote_plus(query.location)
    freshness = f"r{query.freshness_seconds}"
    start = max(page - 1, 0) * 25
    return (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={keyword}&location={location}&f_TPR={freshness}&start={start}"
    )
