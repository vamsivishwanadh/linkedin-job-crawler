from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from src.workbook_jobs import WorkbookJob

MIN_JD_LENGTH = 200


@dataclass(frozen=True)
class JobContext:
    title: str
    company: str
    jd_text: str
    source: str
    job_id: str | None = None
    job_url: str | None = None


def jd_from_workbook_job(job: WorkbookJob) -> JobContext:
    text = job.description.strip()
    if len(text) < MIN_JD_LENGTH:
        raise ValueError(
            f"Job {job.job_id} has no usable description in the workbook "
            f"({len(text)} chars). Paste the JD with --jd-file or --jd-paste."
        )
    return JobContext(
        title=job.title or "Role",
        company=job.company or "Company",
        jd_text=text,
        source="workbook",
        job_id=job.job_id,
        job_url=job.job_url,
    )


def jd_from_file(path: Path, title: str | None, company: str | None) -> JobContext:
    if not path.is_file():
        raise FileNotFoundError(f"JD file not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if len(text) < MIN_JD_LENGTH:
        raise ValueError(f"JD file is too short ({len(text)} chars). Need a full job description.")
    return JobContext(
        title=(title or "Role").strip(),
        company=(company or "Company").strip(),
        jd_text=text,
        source="file",
    )


def jd_from_stdin(title: str | None, company: str | None) -> JobContext:
    print("Paste the job description. End with Ctrl+Z then Enter on Windows, or Ctrl+D on Unix.", file=sys.stderr)
    text = sys.stdin.read().strip()
    if len(text) < MIN_JD_LENGTH:
        raise ValueError(f"Pasted JD is too short ({len(text)} chars). Need a full job description.")
    return JobContext(
        title=(title or "Role").strip(),
        company=(company or "Company").strip(),
        jd_text=text,
        source="stdin",
    )
