from __future__ import annotations

from src.resume.models import ContactInfo, ExperienceBullet, ExperienceEntry, TailoredResume
from src.resume.validate import validate_tailored_resume

MASTER = """
Jane Doe
Software Engineer at Acme Corp built Python APIs and AWS deployments.
Skills: Python, AWS, PostgreSQL.
"""


def test_validation_passes_with_evidence() -> None:
    tailored = TailoredResume(
        contact=ContactInfo(name="Jane Doe"),
        summary="Engineer with Python experience.",
        skills=["Python", "AWS"],
        experience=[
            ExperienceEntry(
                company="Acme Corp",
                title="Software Engineer",
                start_date="2020",
                end_date="Present",
                bullets=[
                    ExperienceBullet(
                        text="Built Python APIs.",
                        evidence="built Python APIs",
                    )
                ],
            )
        ],
    )
    result = validate_tailored_resume(tailored, MASTER, strict=False)
    assert result.status in ("passed", "warnings")


def test_validation_fails_bad_evidence() -> None:
    tailored = TailoredResume(
        contact=ContactInfo(),
        summary="Summary",
        skills=[],
        experience=[
            ExperienceEntry(
                company="Fake Inc",
                title="CTO",
                start_date="2099",
                end_date=None,
                bullets=[
                    ExperienceBullet(
                        text="Invented quantum blockchain.",
                        evidence="quantum blockchain invention",
                    )
                ],
            )
        ],
    )
    result = validate_tailored_resume(tailored, MASTER, strict=True)
    assert result.status == "failed"
