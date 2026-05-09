from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class BrowserOptions:
    headless: bool = True
    slow_mo_ms: int = 0
    profile_dir: str = ".browser-profile"
    linkedin_email: str = ""
    linkedin_password: str = ""


class BrowserSession:
    def __init__(self, options: BrowserOptions):
        self.options = options
        self._playwright = None
        self._browser = None
        self._context = None

    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "Playwright is required for browser-based collection. Install dependencies first."
            ) from exc

        self._playwright = sync_playwright().start()
        profile_dir = Path(self.options.profile_dir)
        profile_dir.mkdir(parents=True, exist_ok=True)
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=self.options.headless,
            slow_mo=self.options.slow_mo_ms,
        )
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._context is not None:
            self._context.close()
        if self._playwright is not None:
            self._playwright.stop()

    def new_page(self):
        if self._context is None:
            raise RuntimeError("BrowserSession is not initialized. Use it as a context manager.")
        return self._context.new_page()

    def ensure_linkedin_login(self) -> None:
        if self._context is None:
            raise RuntimeError("BrowserSession is not initialized. Use it as a context manager.")
        if not self.options.linkedin_email or not self.options.linkedin_password:
            return

        page = self._context.new_page()
        try:
            page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(1500)

            if page.locator("input[name='session_key']").count() == 0:
                return

            page.fill("input[name='session_key']", self.options.linkedin_email)
            page.fill("input[name='session_password']", self.options.linkedin_password)
            page.click("button[type='submit']")
            page.wait_for_load_state("domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
        finally:
            page.close()
