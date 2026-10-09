from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from src.resume.models import ContactInfo, TailoredResume
from src.resume.pdf import render_resume_pdf


def test_pdf_non_empty(tmp_path: Path) -> None:
    tailored = TailoredResume(
        contact=ContactInfo(name="Jane Doe", email="jane@example.com"),
        summary="Experienced software engineer.",
        skills=["Python"],
        experience=[],
        education=[],
    )
    out = tmp_path / "resume.pdf"
    render_resume_pdf(tailored, out)
    assert out.stat().st_size > 500
    reader = PdfReader(str(out))
    text = "".join(page.extract_text() or "" for page in reader.pages)
    assert "Jane Doe" in text
    assert "Professional Summary" in text
