from __future__ import annotations

from src.resume.models import JobAnalysis


def test_coerce_domain_string_and_experience_list() -> None:
    raw = {
        "domain": "Software Development",
        "experience_requirements": [
            "6 to 12 years of hands-on experience",
            "enterprise-grade applications.",
        ],
        "mandatory_skills": "Java",
    }
    model = JobAnalysis.model_validate(raw)
    assert model.domain == ["Software Development"]
    assert "6 to 12 years" in (model.experience_requirements or "")
    assert model.mandatory_skills == ["Java"]
