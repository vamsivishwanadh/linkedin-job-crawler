from __future__ import annotations

from src.resume.models import TailoredResume


def test_tailored_resume_llm_field_aliases() -> None:
    raw = {
        "contact": {"name": "Jane Doe"},
        "summary": "Summary text.",
        "skills": ["Java"],
        "experience": [
            {
                "job_title": "Senior Backend Engineer",
                "company": "Acme",
                "bullets": [
                    {"description": "Built APIs.", "evidence": "Built APIs"},
                ],
            }
        ],
        "education": {
            "degree": "Bachelor of Technology in Engineering",
            "year": 2016,
            "institution": "Example University",
        },
    }
    model = TailoredResume.model_validate(raw)
    assert model.experience[0].title == "Senior Backend Engineer"
    assert model.experience[0].bullets[0].text == "Built APIs."
    assert len(model.education) == 1
    assert model.education[0].degree is not None
