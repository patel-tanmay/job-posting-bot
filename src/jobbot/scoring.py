from __future__ import annotations

from .models import JobPosting, SearchProfile


def score_job(job: JobPosting, profile: SearchProfile) -> float:
    score = 0.0
    haystack = " ".join(
        [job.title, job.company, job.location, job.summary, job.remote_type, job.query]
    ).lower()

    for keyword in profile.keywords:
        if keyword.lower() in haystack:
            score += 3.0

    for location in profile.locations:
        if location.lower() in haystack:
            score += 1.5

    if profile.remote_preference and "remote" in haystack:
        score += 2.0

    if job.source.lower() == "linkedin":
        score += 0.5

    if len(job.summary) > 0:
        score += 0.2

    return round(score, 3)
