from __future__ import annotations

import re

from src.resume.fuzzy_match import normalize_text, skill_match_confidence
from src.resume.models import (
    SkillMatchResult,
    TailoredResume,
    ValidationIssue,
    ValidationResult,
)

_WHITESPACE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return normalize_text(text)


def _evidence_in_resume(evidence: str, master_resume: str) -> bool:
    ev = _normalize(evidence)
    if len(ev) < 8:
        return False
    body = _normalize(master_resume)
    return ev in body


def validate_tailored_resume(
    tailored: TailoredResume,
    master_resume: str,
    strict: bool = True,
    skill_min_confidence: float = 0.9,
) -> ValidationResult:
    issues: list[ValidationIssue] = []
    skill_matches: list[SkillMatchResult] = []

    for entry in tailored.experience:
        if entry.company and _normalize(entry.company) not in _normalize(master_resume):
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Company '{entry.company}' not found in master resume.",
                    field="experience.company",
                )
            )
        for bullet in entry.bullets:
            if not bullet.evidence.strip():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message="Experience bullet missing evidence quote.",
                        field="experience.bullets",
                    )
                )
            elif not _evidence_in_resume(bullet.evidence, master_resume):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Evidence not found in master resume: {bullet.evidence[:80]}…",
                        field="experience.bullets.evidence",
                    )
                )

    for project in tailored.projects:
        for bullet in project.bullets:
            if not bullet.evidence.strip():
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Project '{project.name}' bullet missing evidence.",
                        field="projects.bullets",
                    )
                )
            elif not _evidence_in_resume(bullet.evidence, master_resume):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Project evidence not found in master resume: {bullet.evidence[:80]}…",
                        field="projects.bullets.evidence",
                    )
                )

    for skill in tailored.skills:
        confidence, matched = skill_match_confidence(skill, master_resume)
        if confidence >= 1.0:
            status = "exact"
        elif confidence >= skill_min_confidence:
            status = "fuzzy"
        else:
            status = "unverified"

        skill_matches.append(
            SkillMatchResult(
                skill=skill,
                confidence=round(confidence, 4),
                matched_text=matched,
                status=status,
            )
        )

        if status == "unverified":
            severity = "error" if strict else "warning"
            issues.append(
                ValidationIssue(
                    severity=severity,
                    message=(
                        f"Skill '{skill}' not supported by master resume "
                        f"(best match confidence {confidence:.0%}"
                        f"{f', near «{matched}»' if matched else ''})."
                    ),
                    field="skills",
                    confidence=round(confidence, 4),
                )
            )
        elif status == "fuzzy":
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=(
                        f"Skill '{skill}' fuzzy-matched to «{matched}» "
                        f"with confidence {confidence:.0%}."
                    ),
                    field="skills",
                    confidence=round(confidence, 4),
                )
            )

    errors = [i for i in issues if i.severity == "error"]
    if errors:
        validation_status = "failed"
    elif issues:
        validation_status = "warnings"
    else:
        validation_status = "passed"
    return ValidationResult(
        status=validation_status,
        issues=issues,
        skill_matches=skill_matches,
    )
