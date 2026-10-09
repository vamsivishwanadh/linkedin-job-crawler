from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from src.resume.models import JobAnalysis, TailoredResume, ValidationResult

_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_filename_part(text: str, max_len: int = 48) -> str:
    cleaned = _UNSAFE.sub("", text.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = cleaned.strip("._")
    if not cleaned:
        cleaned = "Unknown"
    return cleaned[:max_len]


def build_pdf_basename(company: str, title: str) -> str:
    return f"{sanitize_filename_part(company)}_{sanitize_filename_part(title)}"


def resolve_output_pdf(output_dir: Path, basename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate = output_dir / f"{basename}.pdf"
    if not candidate.exists():
        return candidate
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return output_dir / f"{basename}_{stamp}.pdf"


def write_metadata(
    meta_path: Path,
    *,
    job_id: str | None,
    company: str,
    title: str,
    pdf_path: Path,
    master_resume_path: Path,
    model: str,
    validation: ValidationResult,
    source: str,
) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "job_id": job_id,
        "company": company,
        "role": title,
        "pdf_file": str(pdf_path),
        "master_resume": str(master_resume_path),
        "model": model,
        "validation_status": validation.status,
        "validation_issues": [i.model_dump() for i in validation.issues],
    }
    meta_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_preview_json(
    path: Path,
    analysis: JobAnalysis,
    tailored: TailoredResume,
    validation: ValidationResult,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "analysis": analysis.model_dump(),
        "tailored_resume": tailored.model_dump(),
        "validation": validation.model_dump(),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
