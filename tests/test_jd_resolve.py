from __future__ import annotations

from pathlib import Path

import pytest

from src.jd_resolve import jd_from_file
from src.workbook_jobs import WorkbookJob


def test_jd_from_file(tmp_path: Path) -> None:
    text = "Role overview.\n" + ("requirements " * 40)
    path = tmp_path / "jd.txt"
    path.write_text(text, encoding="utf-8")
    ctx = jd_from_file(path, "Engineer", "Co")
    assert ctx.company == "Co"
    assert len(ctx.jd_text) >= 200


def test_workbook_job_short_description() -> None:
    from src.jd_resolve import jd_from_workbook_job

    job = WorkbookJob(
        job_id="1",
        title="T",
        company="C",
        location=None,
        description="short",
        job_url=None,
        match_score=None,
        row_index=0,
    )
    with pytest.raises(ValueError, match="no usable description"):
        jd_from_workbook_job(job)
