from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.jd_resolve import JobContext
from src.matching import load_resume_text
from src.resume.analysis import analyze_job_description
from src.resume.llm import LlmConfig, get_openai_client
from src.resume.models import JobAnalysis, TailoredResume, ValidationResult
from src.resume.output import (
    build_pdf_basename,
    resolve_output_pdf,
    write_metadata,
    write_preview_json,
)
from src.resume.pdf import render_resume_pdf
from src.resume.tailor import tailor_resume
from src.resume.validate import validate_tailored_resume


@dataclass(frozen=True)
class ResumeGenerationResult:
    pdf_path: Path | None
    preview_path: Path | None
    meta_path: Path | None
    analysis: JobAnalysis
    tailored: TailoredResume
    validation: ValidationResult


def generate_resume(
    *,
    job: JobContext,
    master_resume_path: Path,
    output_dir: Path,
    model: str | None = None,
    preview_only: bool = False,
    strict_validation: bool = True,
    allow_warnings_pdf: bool = True,
    skill_min_confidence: float = 0.9,
) -> ResumeGenerationResult:
    master = load_resume_text(master_resume_path)
    llm_config = LlmConfig.from_env(model)
    client = get_openai_client()

    analysis = analyze_job_description(client, llm_config, job)
    title = job.title or analysis.job_title or "Role"
    company = job.company or analysis.company or "Company"

    tailored = tailor_resume(client, llm_config, master, analysis, title, company)
    validation = validate_tailored_resume(
        tailored,
        master,
        strict=strict_validation,
        skill_min_confidence=skill_min_confidence,
    )

    basename = build_pdf_basename(company, title)
    preview_path = output_dir / f"{basename}.preview.json"
    write_preview_json(preview_path, analysis, tailored, validation)

    pdf_path: Path | None = None
    meta_path: Path | None = None

    if validation.status == "failed":
        return ResumeGenerationResult(
            pdf_path=None,
            preview_path=preview_path,
            meta_path=None,
            analysis=analysis,
            tailored=tailored,
            validation=validation,
        )

    if preview_only:
        return ResumeGenerationResult(
            pdf_path=None,
            preview_path=preview_path,
            meta_path=None,
            analysis=analysis,
            tailored=tailored,
            validation=validation,
        )

    if validation.status == "warnings" and not allow_warnings_pdf:
        return ResumeGenerationResult(
            pdf_path=None,
            preview_path=preview_path,
            meta_path=None,
            analysis=analysis,
            tailored=tailored,
            validation=validation,
        )

    pdf_path = resolve_output_pdf(output_dir, basename)
    render_resume_pdf(tailored, pdf_path)
    meta_path = pdf_path.with_suffix(".meta.json")
    write_metadata(
        meta_path,
        job_id=job.job_id,
        company=company,
        title=title,
        pdf_path=pdf_path,
        master_resume_path=master_resume_path,
        model=llm_config.model,
        validation=validation,
        source=job.source,
    )

    return ResumeGenerationResult(
        pdf_path=pdf_path,
        preview_path=preview_path,
        meta_path=meta_path,
        analysis=analysis,
        tailored=tailored,
        validation=validation,
    )
