from __future__ import annotations

from typing import List

from bs4 import BeautifulSoup

from ..models import JobPosting, QuerySpec
from ..query_builder import build_linkedin_url
from ..parsers import extract_job_fields
from ..services.browser import BrowserOptions, BrowserSession
from ..utils import sha256_hex
from .base import JobSourceAdapter


class LinkedInJobsAdapter(JobSourceAdapter):
    source_name = "linkedin"

    def __init__(self, browser_options: BrowserOptions):
        self.browser_options = browser_options

    def search(self, query: QuerySpec, max_results: int, max_pages: int = 1) -> List[JobPosting]:
        max_pages = max(1, max_pages)
        jobs: List[JobPosting] = []
        seen = set()

        with BrowserSession(self.browser_options) as browser:
            browser.ensure_linkedin_login()

            for page_number in range(1, max_pages + 1):
                url = build_linkedin_url(query, page=page_number)
                page = browser.new_page()
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(3000)
                    html = page.content()
                finally:
                    page.close()

                soup = BeautifulSoup(html, "html.parser")

                page_added = 0
                for anchor in soup.select("a[href*='/jobs/view/']"):
                    card = anchor.find_parent(["li", "article", "div"]) or anchor.parent
                    card_text = card.get_text("\n", strip=True) if card else anchor.get_text("\n", strip=True)
                    title, company, location = extract_job_fields(
                        card_text,
                        title_hint=anchor.get_text(" ", strip=True),
                        company_hint="",
                        location_hint=query.location,
                    )
                    href = anchor.get("href") or ""
                    if not title or href in seen:
                        continue
                    seen.add(href)
                    jobs.append(
                        JobPosting(
                            source=self.source_name,
                            title=title,
                            company=company or "Unknown",
                            location=location or query.location,
                            url=href if href.startswith("http") else f"https://www.linkedin.com{href}",
                            query=query.keyword,
                            summary="",
                            posted_at="recent",
                            raw={"source_url": url, "card_text": card_text},
                            fingerprint=sha256_hex(f"{title}|{company}|{location}|{href}|linkedin"),
                        )
                    )
                    page_added += 1
                    if len(jobs) >= max_results:
                        return jobs

                if page_added == 0:
                    break

        return jobs
