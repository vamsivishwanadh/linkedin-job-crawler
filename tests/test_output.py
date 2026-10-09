from __future__ import annotations

from pathlib import Path

from src.resume.output import build_pdf_basename, resolve_output_pdf


def test_no_silent_overwrite(tmp_path: Path) -> None:
    base = build_pdf_basename("Acme", "Engineer")
    first = resolve_output_pdf(tmp_path, base)
    first.write_bytes(b"%PDF-1.4")
    second = resolve_output_pdf(tmp_path, base)
    assert second != first
    assert second.name.startswith(base)
