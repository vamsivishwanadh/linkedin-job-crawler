from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.export import EXPORT_COLUMNS
from src.workbook_jobs import get_job_by_id, list_workbook_jobs


@pytest.fixture
def sample_workbook(tmp_path: Path) -> Path:
    path = tmp_path / "jobs.xlsx"
    desc = "x" * 250
    row = {col: None for col in EXPORT_COLUMNS}
    row.update(
        {
            "match_score": 0.42,
            "title": "Backend Engineer",
            "companyName": "Acme Corp",
            "location": "Remote",
            "description": desc,
            "jobUrl": "https://example.com/job/1",
            "id": 12345,
        }
    )
    df = pd.DataFrame([row], columns=EXPORT_COLUMNS)
    df.to_excel(path, sheet_name="jobs", index=False)
    return path


def test_get_job_by_id(sample_workbook: Path) -> None:
    job = get_job_by_id(sample_workbook, "jobs", "12345")
    assert job.job_id == "12345"
    assert job.title == "Backend Engineer"
    assert len(job.description) >= 200


def test_missing_job(sample_workbook: Path) -> None:
    with pytest.raises(LookupError):
        get_job_by_id(sample_workbook, "jobs", "99999")


def test_list_jobs(sample_workbook: Path) -> None:
    jobs = list_workbook_jobs(sample_workbook, "jobs")
    assert len(jobs) == 1
