from jobbot.parsers import (
    extract_job_fields,
    is_us_location,
    location_matches_config,
    looks_like_location,
    should_keep_location,
    title_has_excluded_terms,
)


def test_extract_job_fields_prefers_title_company_location_order():
    text = "Senior Data Engineer\nAcme Corp\nBoston, MA\nFull-time"
    title, company, location = extract_job_fields(text, location_hint="Remote")
    assert title == "Senior Data Engineer"
    assert company == "Acme Corp"
    assert location == "Boston, MA"


def test_extract_job_fields_falls_back_to_location_hint():
    text = "Software Engineer\nExample Inc"
    title, company, location = extract_job_fields(text, location_hint="New York, NY")
    assert title == "Software Engineer"
    assert company == "Example Inc"
    assert location == "New York, NY"


def test_looks_like_location_identifies_remote_and_city():
    assert looks_like_location("Remote")
    assert looks_like_location("Boston, MA")
    assert not looks_like_location("Acme Corp")


def test_title_has_excluded_terms_blocks_seniority_titles():
    assert title_has_excluded_terms("Senior Data Engineer", ["senior"])
    assert title_has_excluded_terms("Data Engineer II", ["ii"])
    assert title_has_excluded_terms("Engineering Manager", ["manager"])
    assert title_has_excluded_terms("Data Science Manager", ["Data Science Manager"])
    assert title_has_excluded_terms("AD data science job posting", ["ad"])
    assert not title_has_excluded_terms("Data Engineer", ["senior", "manager", "ii", "iii", "ad"])


def test_location_matching_prefers_config_then_us_fallback():
    configs = ["Boston, MA", "Remote"]
    assert location_matches_config("Boston, MA", configs)
    assert should_keep_location("Boston, MA", configs)
    assert should_keep_location("San Francisco, CA", configs)
    assert should_keep_location("Remote - US", configs)
    assert not should_keep_location("Toronto, Canada", configs)
    assert not should_keep_location("Bengaluru, India", configs)


def test_us_location_detection_handles_common_us_forms():
    assert is_us_location("Boston, MA")
    assert is_us_location("Remote")
    assert is_us_location("New York, NY 10001")
    assert is_us_location("United States")
    assert is_us_location("U.S.")
    assert is_us_location("USA")
    assert not is_us_location("Toronto, Canada")
