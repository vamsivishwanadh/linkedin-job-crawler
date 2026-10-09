from __future__ import annotations

from enum import Enum
from typing import Literal

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.resume.coerce import (
    as_optional_str,
    as_str_list,
    normalize_tailored_resume_payload,
)


class ContactInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None


class ExperienceBullet(BaseModel):
    text: str
    evidence: str = Field(
        description="Verbatim phrase from the master resume supporting this bullet.",
    )


class ExperienceEntry(BaseModel):
    company: str
    title: str
    location: str | None = None
    start_date: str
    end_date: str | None = None
    bullets: list[ExperienceBullet] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str
    bullets: list[ExperienceBullet] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str
    degree: str | None = None
    dates: str | None = None
    details: str | None = None


class JobAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    job_title: str | None = None
    company: str | None = None
    mandatory_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    experience_requirements: str | None = None
    seniority: str | None = None
    domain: list[str] = Field(default_factory=list)
    ats_keywords: list[str] = Field(default_factory=list)

    @field_validator(
        "mandatory_skills",
        "preferred_skills",
        "responsibilities",
        "domain",
        "ats_keywords",
        mode="before",
    )
    @classmethod
    def _list_fields(cls, value: Any) -> list[str]:
        return as_str_list(value)

    @field_validator(
        "job_title",
        "company",
        "experience_requirements",
        "seniority",
        mode="before",
    )
    @classmethod
    def _str_fields(cls, value: Any) -> str | None:
        return as_optional_str(value)


class TailoredResume(BaseModel):
    model_config = ConfigDict(extra="ignore")

    contact: ContactInfo
    summary: str
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _normalize_llm_shape(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        exp = data.get("experience")
        if isinstance(exp, list) and exp and not isinstance(exp[0], dict):
            return data
        edu = data.get("education")
        if isinstance(edu, list) and edu and not isinstance(edu[0], dict):
            return data
        return normalize_tailored_resume_payload(data)

    @field_validator("skills", "certifications", mode="before")
    @classmethod
    def _tailor_lists(cls, value: Any) -> list[str]:
        return as_str_list(value)

    @field_validator("summary", mode="before")
    @classmethod
    def _summary_str(cls, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return "\n".join(as_str_list(value))
        return str(value).strip()


class ValidationIssue(BaseModel):
    severity: Literal["error", "warning"]
    message: str
    field: str | None = None
    confidence: float | None = None


class SkillMatchResult(BaseModel):
    skill: str
    confidence: float
    matched_text: str | None = None
    status: Literal["exact", "fuzzy", "unverified"]


class ValidationResult(BaseModel):
    status: Literal["passed", "warnings", "failed"]
    issues: list[ValidationIssue] = Field(default_factory=list)
    skill_matches: list[SkillMatchResult] = Field(default_factory=list)


class GenerationStatus(str, Enum):
    PASSED = "passed"
    WARNINGS = "warnings"
    FAILED = "failed"
