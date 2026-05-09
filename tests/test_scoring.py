from jobbot.models import JobPosting, SearchProfile, SourceSettings
from jobbot.scoring import score_job


def test_scoring_reacts_to_keyword_and_remote_preference():
    profile = SearchProfile(
        name="default",
        keywords=["data engineer"],
        locations=["Remote"],
        sources={"linkedin": SourceSettings()},
        remote_preference=True,
    )
    job = JobPosting(
        source="linkedin",
        title="Senior Data Engineer",
        company="Example",
        location="Remote",
        url="https://example.com",
        summary="Remote first role",
    )
    assert score_job(job, profile) > 0
