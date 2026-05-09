from __future__ import annotations

import re
from typing import Iterable, List, Tuple


_LOCATION_HINTS = (
    "remote",
    "hybrid",
    "onsite",
)

_STATE_ABBREVIATIONS = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY",
    "LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND",
    "OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC",
}

_NON_US_LOCATION_MARKERS = {
    "canada",
    "united kingdom",
    "uk",
    "india",
    "germany",
    "france",
    "spain",
    "italy",
    "netherlands",
    "belgium",
    "sweden",
    "norway",
    "finland",
    "denmark",
    "ireland",
    "australia",
    "new zealand",
    "singapore",
    "japan",
    "china",
    "mexico",
    "brazil",
    "argentina",
    "chile",
    "colombia",
    "peru",
    "south africa",
    "philippines",
    "pakistan",
    "bangladesh",
    "sri lanka",
    "uae",
    "saudi arabia",
    "dubai",
    "europe",
}

_US_STATE_FULL_NAMES = {
    "alabama",
    "alaska",
    "arizona",
    "arkansas",
    "california",
    "colorado",
    "connecticut",
    "delaware",
    "florida",
    "georgia",
    "hawaii",
    "idaho",
    "illinois",
    "indiana",
    "iowa",
    "kansas",
    "kentucky",
    "louisiana",
    "maine",
    "maryland",
    "massachusetts",
    "michigan",
    "minnesota",
    "mississippi",
    "missouri",
    "montana",
    "nebraska",
    "nevada",
    "new hampshire",
    "new jersey",
    "new mexico",
    "new york",
    "north carolina",
    "north dakota",
    "ohio",
    "oklahoma",
    "oregon",
    "pennsylvania",
    "rhode island",
    "south carolina",
    "south dakota",
    "tennessee",
    "texas",
    "utah",
    "vermont",
    "virginia",
    "washington",
    "west virginia",
    "wisconsin",
    "wyoming",
    "district of columbia",
    "washington dc",
}


def clean_lines(text: str) -> List[str]:
    if not text:
        return []
    raw_lines = re.split(r"[\n\r|]+", text)
    lines: List[str] = []
    for raw in raw_lines:
        line = " ".join(raw.split()).strip(" \t-–•·")
        if line:
            lines.append(line)
    deduped: List[str] = []
    for line in lines:
        if not deduped or deduped[-1].lower() != line.lower():
            deduped.append(line)
    return deduped


def normalize_location_text(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.strip().lower()).split())


def looks_like_location(value: str) -> bool:
    text = value.strip().lower()
    if not text:
        return False
    if any(hint in text for hint in _LOCATION_HINTS):
        return True
    if re.search(r"\b[A-Z]{2}\b", value):
        return True
    if "," in value:
        return True
    if re.search(r"\b\d{5}\b", value):
        return True
    return False


def extract_job_fields(
    text: str,
    *,
    title_hint: str = "",
    company_hint: str = "",
    location_hint: str = "",
) -> Tuple[str, str, str]:
    lines = clean_lines(text)
    if not lines:
        return title_hint.strip(), company_hint.strip(), location_hint.strip()

    title = title_hint.strip() or lines[0]
    remaining = [line for line in lines if line.lower() != title.lower()]

    location = ""
    company = ""

    for line in remaining:
        if looks_like_location(line):
            location = line
            break

    company_candidates = [line for line in remaining if line != location]
    for line in company_candidates:
        if line != title and not looks_like_location(line):
            company = line
            break

    if not company and company_hint.strip():
        company = company_hint.strip()
    if not location and location_hint.strip():
        location = location_hint.strip()

    if not title and company_candidates:
        title = company_candidates[0]

    return title.strip(), company.strip(), location.strip()


def title_has_excluded_terms(title: str, excluded_terms: List[str]) -> bool:
    normalized_title = " ".join(title.strip().lower().split())
    for term in excluded_terms:
        normalized = " ".join(term.strip().lower().split())
        if not normalized:
            continue
        pattern = rf"\b{re.escape(normalized)}\b"
        if re.search(pattern, normalized_title, flags=re.IGNORECASE):
            return True
    return False


def location_matches_config(location: str, configured_locations: Iterable[str]) -> bool:
    normalized_location = normalize_location_text(location)
    if not normalized_location:
        return False
    for configured in configured_locations:
        if normalized_location == normalize_location_text(configured):
            return True
    return False


def is_us_location(location: str) -> bool:
    normalized = normalize_location_text(location)
    if not normalized:
        return False

    if any(re.search(rf"\b{re.escape(marker)}\b", normalized) for marker in _NON_US_LOCATION_MARKERS):
        return False

    if "remote" in normalized:
        return True
    if "united states" in normalized:
        return True
    if re.search(r"\b(u\s+s\s+a?|u\s+s|usa)\b", normalized):
        return True
    if re.search(r"\b\d{5}(?:-\d{4})?\b", location):
        return True
    if re.search(r"\b(" + "|".join(sorted(_STATE_ABBREVIATIONS)) + r")\b", location):
        return True
    if any(state in normalized for state in _US_STATE_FULL_NAMES):
        return True
    if normalized in {"washington d c", "district of columbia"}:
        return True

    return False


def should_keep_location(location: str, configured_locations: Iterable[str]) -> bool:
    return location_matches_config(location, configured_locations) or is_us_location(location)
