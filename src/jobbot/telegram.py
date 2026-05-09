from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Iterable, List

import requests

from .models import JobPosting


@dataclass(slots=True)
class TelegramConfig:
    bot_token: str
    chat_id: str


class TelegramNotifier:
    def __init__(self, config: TelegramConfig):
        self.config = config

    def send_message(self, text: str) -> None:
        if not self.config.bot_token or not self.config.chat_id:
            raise RuntimeError("Telegram bot token and chat id must be configured.")
        url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": self.config.chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        response.raise_for_status()


def format_digest(title: str, jobs: Iterable[JobPosting], max_items: int = 10) -> str:
    items = list(jobs)[:max_items]
    if not items:
        return f"{html.escape(title)}\n\nNo new jobs found."

    lines: List[str] = [f"<b>{html.escape(title)}</b>", ""]
    for index, job in enumerate(items, start=1):
        lines.append(f"{index}. <b>{html.escape(job.title)}</b>")
        lines.append(
            "   "
            + " | ".join(
                [
                    html.escape(job.company or "Unknown"),
                    html.escape(job.location or "Unknown"),
                ]
            )
        )
        lines.append(f'   <a href="{html.escape(job.url, quote=True)}">Open link</a>')
        lines.append("")
    return "\n".join(lines)
