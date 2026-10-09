from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.jd_resolve import JobContext
from src.resume.models import ContactInfo, JobAnalysis, TailoredResume, ValidationResult
from src.resume.pipeline import generate_resume

MASTER = Path(__file__).resolve().parent / "fixtures" / "master_resume.txt"
JD = "Senior Python engineer. " * 30


@patch("src.resume.pipeline.get_openai_client")
@patch("src.resume.pipeline.analyze_job_description")
@patch("src.resume.pipeline.tailor_resume")
def test_pipeline_mocked(
    mock_tailor,
    mock_analyze,
    mock_client,
    tmp_path: Path,
) -> None:
    mock_client.return_value = MagicMock()
    mock_analyze.return_value = JobAnalysis(job_title="Engineer", company="Acme")
    mock_tailor.return_value = TailoredResume(
        contact=ContactInfo(name="Jane Doe"),
        summary="Python engineer at Acme Corp with AWS experience.",
        skills=["Python"],
        experience=[],
    )
    MASTER.parent.mkdir(parents=True, exist_ok=True)
    MASTER.write_text(
        "Jane Doe\nPython engineer at Acme Corp with AWS experience.\n",
        encoding="utf-8",
    )
    job = JobContext(
        title="Engineer",
        company="Acme",
        jd_text=JD,
        source="test",
    )
    result = generate_resume(
        job=job,
        master_resume_path=MASTER,
        output_dir=tmp_path,
        model="test-model",
        preview_only=False,
        strict_validation=False,
    )
    assert result.pdf_path is not None
    assert result.pdf_path.exists()
