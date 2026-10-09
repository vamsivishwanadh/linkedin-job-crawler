from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.config import load_app_config
from src.jd_resolve import JobContext, jd_from_file, jd_from_stdin, jd_from_workbook_job
from src.resume.pipeline import generate_resume
from src.workbook_jobs import get_job_by_id, list_workbook_jobs

log = logging.getLogger(__name__)


def run_resume(args: argparse.Namespace) -> int:
    app = load_app_config(args.config)

    if args.list:
        jobs = list_workbook_jobs(
            app.export.excel_path,
            app.export.sheet_name,
            limit=args.list_limit,
        )
        if not jobs:
            log.info("No jobs in workbook.")
            return 0
        for job in jobs:
            score = f"{job.match_score:.3f}" if job.match_score is not None else "n/a"
            log.info(
                "%s | score=%s | %s @ %s",
                job.job_id,
                score,
                job.title,
                job.company,
            )
        return 0

    if args.job_id:
        wb_job = get_job_by_id(
            app.export.excel_path,
            app.export.sheet_name,
            args.job_id,
        )
        job = jd_from_workbook_job(wb_job)
        if args.title or args.company:
            job = JobContext(
                title=args.title or job.title,
                company=args.company or job.company,
                jd_text=job.jd_text,
                source=job.source,
                job_id=job.job_id,
                job_url=job.job_url,
            )
    elif args.jd_file:
        job = jd_from_file(Path(args.jd_file), args.title, args.company)
    elif args.jd_paste:
        job = jd_from_stdin(args.title, args.company)
    else:
        log.error("Specify --job-id, --jd-file, --jd-paste, or --list.")
        return 1

    model = args.model or app.resume.model
    result = generate_resume(
        job=job,
        master_resume_path=app.matching.resume_path,
        output_dir=app.resume.output_dir,
        model=model,
        preview_only=args.preview_only,
        strict_validation=app.resume.strict_validation,
        allow_warnings_pdf=app.resume.allow_warnings_pdf,
        skill_min_confidence=app.resume.skill_min_confidence,
    )

    log.info("Preview JSON: %s", result.preview_path)
    for sm in result.validation.skill_matches:
        log.info(
            "  skill %s: %s (confidence %.0f%%%s)",
            sm.skill,
            sm.status,
            sm.confidence * 100,
            f", matched «{sm.matched_text}»" if sm.matched_text else "",
        )
    log.info("Validation: %s (%d issue(s))", result.validation.status, len(result.validation.issues))
    for issue in result.validation.issues:
        log.info("  [%s] %s", issue.severity, issue.message)

    if result.validation.status == "failed":
        log.error("PDF not generated due to validation failures. Review the preview JSON.")
        return 1

    if args.preview_only:
        log.info("Preview-only mode; no PDF written.")
        return 0

    if result.pdf_path:
        log.info("PDF: %s", result.pdf_path)
        if result.meta_path:
            log.info("Metadata: %s", result.meta_path)
        return 0

    log.error("PDF was not generated.")
    return 1


def add_resume_parser(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--job-id", help="LinkedIn job id from the Excel workbook")
    sub.add_argument("--jd-file", type=Path, help="Path to a plain-text job description")
    sub.add_argument("--jd-paste", action="store_true", help="Read JD from stdin")
    sub.add_argument("--title", help="Role title (manual JD or override)")
    sub.add_argument("--company", help="Company name (manual JD or override)")
    sub.add_argument(
        "--preview-only",
        action="store_true",
        help="Run LLM + validation and write preview JSON only (no PDF)",
    )
    sub.add_argument("--model", help="OpenAI model override (default: OPENAI_MODEL or gpt-4o-mini)")
    sub.add_argument("--list", action="store_true", help="List jobs from the workbook")
    sub.add_argument("--list-limit", type=int, default=30, help="Max rows for --list")
