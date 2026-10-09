from __future__ import annotations

from src.resume.fuzzy_match import skill_match_confidence
from src.resume.models import ContactInfo, TailoredResume
from src.resume.validate import validate_tailored_resume

MASTER = "Engineer with Scrum, Kanban, and agile software delivery practices."


def test_agile_substring_match() -> None:
    conf, matched = skill_match_confidence("Agile", MASTER)
    assert conf == 1.0
    assert matched == "agile"


def test_fuzzy_skill_passes_at_90_percent() -> None:
    resume = TailoredResume(
        contact=ContactInfo(),
        summary="x",
        skills=["Agile"],
    )
    result = validate_tailored_resume(resume, MASTER, strict=True, skill_min_confidence=0.9)
    assert result.skill_matches[0].status == "exact"
    assert not any(i.severity == "error" for i in result.issues)


def test_unverified_skill_fails_strict() -> None:
    resume = TailoredResume(
        contact=ContactInfo(),
        summary="x",
        skills=["COBOL"],
    )
    result = validate_tailored_resume(resume, MASTER, strict=True, skill_min_confidence=0.9)
    assert result.skill_matches[0].status == "unverified"
    assert result.status == "failed"
