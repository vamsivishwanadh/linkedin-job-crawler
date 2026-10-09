from __future__ import annotations

from pathlib import Path

import pytest

from src.matching import load_resume_text


def test_missing_resume(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="Resume not found"):
        load_resume_text(tmp_path / "missing.txt")
