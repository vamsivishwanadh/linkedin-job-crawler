from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class ApifySettings:
    actor_id: str
    published_at: str
    company_profile: bool
    enrich_company: bool
    max_rows_per_search: int


@dataclass(frozen=True)
class SearchSettings:
    titles: list[str]
    locations: list[str]
    work_types: list[str]
    contract_types: list[str]
    experience_levels: list[str]
    easy_apply: bool
    under_10_applicants: bool


@dataclass(frozen=True)
class MatchingSettings:
    resume_path: Path
    min_match_score: float
    min_hours_since_posted: float
    max_hours_since_posted: float


@dataclass(frozen=True)
class ExportSettings:
    excel_path: Path
    sheet_name: str
    min_score_to_export: float


@dataclass(frozen=True)
class ResumeGeneratorSettings:
    output_dir: Path
    strict_validation: bool
    allow_warnings_pdf: bool
    skill_min_confidence: float
    model: str | None


@dataclass(frozen=True)
class AppConfig:
    apify: ApifySettings
    search: SearchSettings
    matching: MatchingSettings
    export: ExportSettings
    resume: ResumeGeneratorSettings


@dataclass(frozen=True)
class Settings(AppConfig):
    apify_token: str


def _load_yaml(config_path: Path | None) -> dict:
    path = config_path or (PROJECT_ROOT / "config.yaml")
    if not path.is_file():
        raise RuntimeError(
            f"Config not found at {path}. Copy config.example.yaml to config.yaml and edit it."
        )
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_env_file() -> None:
    """Load project .env; overrides Windows/system OPENAI_API_KEY and APIFY_TOKEN."""
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def load_app_config(config_path: Path | None = None) -> AppConfig:
    load_env_file()
    raw = _load_yaml(config_path)

    apify_raw = raw.get("apify") or {}
    search_raw = raw.get("search") or {}
    match_raw = raw.get("matching") or {}
    export_raw = raw.get("export") or {}
    resume_raw = raw.get("resume") or {}

    resume_rel = match_raw.get("resume_path", "resume/resume.txt")
    resume_path = (PROJECT_ROOT / resume_rel).resolve()
    excel_rel = export_raw.get("excel_path", "data/jobs.xlsx")
    excel_path = (PROJECT_ROOT / excel_rel).resolve()
    out_rel = resume_raw.get("output_dir", "data/resumes")
    output_dir = (PROJECT_ROOT / out_rel).resolve()

    return AppConfig(
        apify=ApifySettings(
            actor_id=apify_raw.get("actor_id", "bebity/linkedin-jobs-scraper"),
            published_at=apify_raw.get("published_at", "r86400"),
            company_profile=bool(apify_raw.get("company_profile", True)),
            enrich_company=bool(apify_raw.get("enrich_company", False)),
            max_rows_per_search=int(apify_raw.get("max_rows_per_search", 100)),
        ),
        search=SearchSettings(
            titles=list(search_raw.get("titles") or []),
            locations=list(search_raw.get("locations") or []),
            work_types=list(search_raw.get("work_types") or []),
            contract_types=list(search_raw.get("contract_types") or []),
            experience_levels=list(search_raw.get("experience_levels") or []),
            easy_apply=bool(search_raw.get("easy_apply", False)),
            under_10_applicants=bool(search_raw.get("under_10_applicants", False)),
        ),
        matching=MatchingSettings(
            resume_path=resume_path,
            min_match_score=float(match_raw.get("min_match_score", 0.12)),
            min_hours_since_posted=float(match_raw.get("min_hours_since_posted", 0)),
            max_hours_since_posted=float(match_raw.get("max_hours_since_posted", 24)),
        ),
        export=ExportSettings(
            excel_path=excel_path,
            sheet_name=str(export_raw.get("sheet_name", "jobs")),
            min_score_to_export=float(export_raw.get("min_score_to_export", 0.12)),
        ),
        resume=ResumeGeneratorSettings(
            output_dir=output_dir,
            strict_validation=bool(resume_raw.get("strict_validation", True)),
            allow_warnings_pdf=bool(resume_raw.get("allow_warnings_pdf", True)),
            skill_min_confidence=float(resume_raw.get("skill_min_confidence", 0.9)),
            model=resume_raw.get("model"),
        ),
    )


def load_settings(
    config_path: Path | None = None,
    *,
    require_apify_token: bool = True,
) -> Settings:
    app = load_app_config(config_path)
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if require_apify_token and not token:
        raise RuntimeError(
            "APIFY_TOKEN is missing. Copy .env.example to .env and set your Apify API token."
        )
    return Settings(apify_token=token, **app.__dict__)
