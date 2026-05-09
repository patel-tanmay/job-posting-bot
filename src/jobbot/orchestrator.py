from __future__ import annotations

from typing import Dict, Iterable, List

from .adapters.linkedin import LinkedInJobsAdapter
from .models import AppConfig, JobPosting, QuerySpec, SearchProfile
from .services.browser import BrowserOptions
from .storage.sqlite_store import SqliteJobStore
from .telegram import TelegramConfig, TelegramNotifier, format_digest
from .utils import sha256_hex
from .parsers import should_keep_location, title_has_excluded_terms


MAX_TOTAL_POSTINGS = 20


def build_queries(profile: SearchProfile) -> List[QuerySpec]:
    queries: List[QuerySpec] = []
    for keyword in profile.keywords:
        for location in profile.locations:
            for source_name, source_settings in profile.sources.items():
                if not source_settings.enabled:
                    continue
                queries.append(
                    QuerySpec(
                        keyword=keyword,
                        location=location,
                        freshness_hours=source_settings.freshness_hours,
                        max_results=source_settings.max_results,
                        source=source_name,
                    )
                )
    return queries


class JobSearchOrchestrator:
    def __init__(self, config: AppConfig):
        self.config = config
        self.store = SqliteJobStore(config.state_db_path)
        browser_options = BrowserOptions(
            headless=config.browser_headless,
            slow_mo_ms=config.browser_slow_mo_ms,
            profile_dir=config.browser_profile_dir,
            linkedin_email=config.linkedin_email,
            linkedin_password=config.linkedin_password,
        )
        self.adapters: Dict[str, object] = {
            "linkedin": LinkedInJobsAdapter(browser_options),
        }
        self.telegram = TelegramNotifier(
            TelegramConfig(
                bot_token=config.telegram_bot_token,
                chat_id=config.telegram_chat_id,
            )
        )

    def run_profile(self, profile: SearchProfile) -> List[JobPosting]:
        collected: List[JobPosting] = []
        for query in build_queries(profile):
            adapter = self.adapters.get(query.source)
            if adapter is None:
                continue
            jobs = adapter.search(query, query.max_results, self.config.browser_max_pages)  # type: ignore[attr-defined]
            for job in jobs:
                if title_has_excluded_terms(job.title, profile.title_exclude_terms):
                    continue
                if not should_keep_location(job.location, profile.locations):
                    continue
                if not job.fingerprint:
                    job.fingerprint = sha256_hex(job.identity_key())
                collected.append(job)

        unique: Dict[str, JobPosting] = {}
        for job in collected:
            unique.setdefault(job.fingerprint, job)

        fresh: List[JobPosting] = []
        for job in unique.values():
            if self.store.has_seen(job.fingerprint):
                continue
            fresh.append(job)

        return fresh

    def collect_fresh_jobs(self) -> List[JobPosting]:
        collected: List[JobPosting] = []
        seen_fingerprints = set()

        for profile in self.config.profiles:
            for job in self.run_profile(profile):
                if job.fingerprint in seen_fingerprints:
                    continue
                seen_fingerprints.add(job.fingerprint)
                collected.append(job)
                if len(collected) >= MAX_TOTAL_POSTINGS:
                    return collected[:MAX_TOTAL_POSTINGS]

        return collected[:MAX_TOTAL_POSTINGS]

    def mark_seen(self, jobs: Iterable[JobPosting]) -> None:
        self.store.mark_seen(jobs)

    def run_and_notify(self) -> List[JobPosting]:
        all_fresh = self.collect_fresh_jobs()
        message = format_digest(self.config.telegram_message_title, all_fresh, max_items=MAX_TOTAL_POSTINGS)
        if all_fresh:
            self.telegram.send_message(message)
            self.mark_seen(all_fresh)
        return all_fresh
