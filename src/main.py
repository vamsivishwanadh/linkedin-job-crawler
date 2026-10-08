from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.apify_jobs import fetch_jobs, fetch_jobs_from_run
from src.config import load_settings
from src.export import append_to_excel
from src.matching import attach_match_scores, load_resume_text
from src.time_filter import is_within_hours

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def run(
    config_path: Path | None = None,
    dry_run: bool = False,
    apify_run_id: str | None = None,
) -> int:
    settings = load_settings(config_path)
    resume_text = load_resume_text(settings.matching.resume_path)

    if dry_run:
        log.info("Dry run: skipping Apify call")
        return 0

    if apify_run_id:
        log.info("Loading jobs from Apify run %s (no new scrape)", apify_run_id)
        jobs = fetch_jobs_from_run(settings.apify_token, apify_run_id)
    else:
        log.info("Running Apify actor %s", settings.apify.actor_id)
        jobs = fetch_jobs(settings.apify_token, settings.apify, settings.search)
    log.info("Fetched %d jobs from Apify", len(jobs))

    recent = [
        j
        for j in jobs
        if is_within_hours(
            j,
            settings.matching.min_hours_since_posted,
            settings.matching.max_hours_since_posted,
        )
    ]
    log.info("After time window filter: %d jobs", len(recent))

    scored = attach_match_scores(recent, resume_text)
    matched = [
        j
        for j in scored
        if (j.get("match_score") or 0) >= settings.matching.min_match_score
    ]
    log.info(
        "After resume match (>= %.3f): %d jobs",
        settings.matching.min_match_score,
        len(matched),
    )

    to_export = [
        j
        for j in matched
        if (j.get("match_score") or 0) >= settings.export.min_score_to_export
    ]
    added, total = append_to_excel(
        to_export,
        settings.export.excel_path,
        settings.export.sheet_name,
    )
    log.info("Wrote Excel: %d new rows, %d total rows -> %s", added, total, settings.export.excel_path)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily LinkedIn job crawl via Apify")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.yaml (default: ./config.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and resume without calling Apify",
    )
    parser.add_argument(
        "--apify-run-id",
        default=None,
        help="Re-process a finished Apify run (from logs) without a new scrape",
    )
    args = parser.parse_args()
    try:
        raise SystemExit(
            run(args.config, dry_run=args.dry_run, apify_run_id=args.apify_run_id)
        )
    except Exception as exc:
        log.error("%s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
