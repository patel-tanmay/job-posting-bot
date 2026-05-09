from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
from .orchestrator import JobSearchOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jobbot")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run the job search pipeline once.")
    run.add_argument("--config", required=True, help="Path to YAML config file.")
    run.add_argument("--dry-run", action="store_true", help="Collect and print results only.")

    sample = sub.add_parser("sample-config", help="Print a sample config reference.")
    sample.add_argument("--output", help="Optional file path to write the sample config.")

    return parser


def _write_sample_config(path: str) -> None:
    sample = Path(__file__).resolve().parents[2] / "config.example.yaml"
    text = sample.read_text()
    Path(path).write_text(text)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "sample-config":
        text = (Path(__file__).resolve().parents[2] / "config.example.yaml").read_text()
        if args.output:
            Path(args.output).write_text(text)
        else:
            print(text)
        return 0

    if args.command == "run":
        config = load_config(args.config)
        orchestrator = JobSearchOrchestrator(config)
        if args.dry_run:
            results = orchestrator.collect_fresh_jobs()
            print(
                json.dumps(
                    [
                        {
                            "source": job.source,
                            "title": job.title,
                            "company": job.company,
                            "location": job.location,
                            "url": job.url,
                            "fingerprint": job.fingerprint,
                        }
                        for job in results
                    ],
                    indent=2,
                )
            )
        else:
            results = orchestrator.run_and_notify()
            print(f"Sent {len(results)} new jobs.")
        return 0

    return 1
