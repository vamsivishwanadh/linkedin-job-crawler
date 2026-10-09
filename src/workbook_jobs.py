from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.export import EXPORT_COLUMNS

WORKBOOK_REQUIRED_COLUMNS = [
    "id",
    "title",
    "companyName",
    "description",
    "jobUrl",
]


@dataclass(frozen=True)
class WorkbookJob:
    job_id: str
    title: str
    company: str
    location: str | None
    description: str
    job_url: str | None
    match_score: float | None
    row_index: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.job_id,
            "title": self.title,
            "companyName": self.company,
            "location": self.location,
            "description": self.description,
            "jobUrl": self.job_url,
            "match_score": self.match_score,
        }


def _normalize_id(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise ValueError("Job id is missing.")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    if not text or text.lower() == "nan":
        raise ValueError("Job id is missing.")
    return text


def read_jobs_workbook(excel_path: Path, sheet_name: str) -> pd.DataFrame:
    if not excel_path.is_file():
        raise FileNotFoundError(
            f"Workbook not found: {excel_path}. Run the crawler first or fix export.excel_path in config.yaml."
        )
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    missing = [c for c in WORKBOOK_REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise RuntimeError(
            f"Workbook at {excel_path} is missing required columns: {missing}. "
            f"Expected columns include: {WORKBOOK_REQUIRED_COLUMNS}"
        )
    return df


def list_workbook_jobs(
    excel_path: Path,
    sheet_name: str,
    limit: int = 30,
) -> list[WorkbookJob]:
    df = read_jobs_workbook(excel_path, sheet_name)
    if "match_score" in df.columns:
        df = df.sort_values("match_score", ascending=False, na_position="last")
    jobs: list[WorkbookJob] = []
    for idx, row in df.head(limit).iterrows():
        jobs.append(_row_to_job(row, int(idx)))
    return jobs


def get_job_by_id(excel_path: Path, sheet_name: str, job_id: str) -> WorkbookJob:
    df = read_jobs_workbook(excel_path, sheet_name)
    target = str(job_id).strip()
    if not target:
        raise ValueError("job-id must not be empty.")

    df = df.copy()
    df["_id_norm"] = df["id"].apply(lambda v: _normalize_id(v) if pd.notna(v) else "")
    matches = df[df["_id_norm"] == target]
    if matches.empty:
        raise LookupError(
            f"No job with id '{target}' in {excel_path} (sheet '{sheet_name}'). "
            "Use 'python -m src.main resume --list' to see ids."
        )
    if len(matches) > 1:
        rows = matches.index.tolist()
        raise RuntimeError(
            f"Duplicate job id '{target}' in workbook (rows {rows}). "
            "Fix the Excel file before generating a resume."
        )
    row = matches.iloc[0]
    return _row_to_job(row, int(matches.index[0]))


def _row_to_job(row: pd.Series, row_index: int) -> WorkbookJob:
    job_id = _normalize_id(row["id"])
    title = str(row.get("title") or "").strip()
    company = str(row.get("companyName") or "").strip()
    desc = row.get("description")
    description = str(desc).strip() if pd.notna(desc) else ""
    job_url = row.get("jobUrl")
    url = str(job_url).strip() if pd.notna(job_url) else None
    location_val = row.get("location")
    location = str(location_val).strip() if pd.notna(location_val) else None
    score_val = row.get("match_score")
    score = float(score_val) if pd.notna(score_val) else None
    return WorkbookJob(
        job_id=job_id,
        title=title,
        company=company,
        location=location,
        description=description,
        job_url=url,
        match_score=score,
        row_index=row_index,
    )


def export_columns() -> list[str]:
    return list(EXPORT_COLUMNS)
