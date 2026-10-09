from __future__ import annotations

from typing import Any


def as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if "\n" in text:
            return [line.strip() for line in text.splitlines() if line.strip()]
        return [text]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if item is None:
                continue
            s = str(item).strip()
            if s:
                out.append(s)
        return out
    s = str(value).strip()
    return [s] if s else []


def as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        parts = as_str_list(value)
        return "\n".join(parts) if parts else None
    text = str(value).strip()
    return text or None


def _first_str(data: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        val = data.get(key)
        if val is None:
            continue
        if isinstance(val, str) and val.strip():
            return val.strip()
        if not isinstance(val, str):
            s = str(val).strip()
            if s:
                return s
    return default


def _normalize_bullet(raw: Any) -> dict[str, str]:
    if isinstance(raw, str):
        text = raw.strip()
        return {"text": text, "evidence": text}
    if isinstance(raw, dict):
        text = _first_str(
            raw,
            "text",
            "description",
            "bullet",
            "content",
            "achievement",
        )
        evidence = _first_str(raw, "evidence", "source", "quote", "supporting_text")
        if not evidence and text:
            evidence = text
        return {"text": text, "evidence": evidence}
    text = str(raw).strip()
    return {"text": text, "evidence": text}


def _normalize_bullets(raw: Any) -> list[dict[str, str]]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [_normalize_bullet(raw)]
    if isinstance(raw, list):
        return [_normalize_bullet(item) for item in raw if item is not None]
    return [_normalize_bullet(raw)]


def _normalize_experience_entry(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {
            "company": "Company",
            "title": "Role",
            "start_date": "See resume",
            "bullets": _normalize_bullets(raw),
        }
    dates = _first_str(raw, "dates", "period", "duration")
    start = _first_str(raw, "start_date", "startDate", "from", "start")
    end = _first_str(raw, "end_date", "endDate", "to", "end") or None
    if not start and dates and "–" in dates:
        parts = dates.split("–", 1)
        start = parts[0].strip()
        end = (parts[1].strip() if len(parts) > 1 else None) or end
    elif not start and dates and "-" in dates:
        parts = dates.split("-", 1)
        start = parts[0].strip()
        end = (parts[1].strip() if len(parts) > 1 else None) or end
    if not start:
        start = dates or "See resume"
    return {
        "company": _first_str(raw, "company", "employer", "organization", "org", default="Company"),
        "title": _first_str(
            raw,
            "title",
            "job_title",
            "jobTitle",
            "role",
            "position",
            default="Role",
        ),
        "location": _first_str(raw, "location", "city") or None,
        "start_date": start,
        "end_date": end,
        "bullets": _normalize_bullets(
            raw.get("bullets")
            or raw.get("responsibilities")
            or raw.get("achievements")
            or raw.get("highlights")
        ),
    }


def _normalize_project_entry(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {"name": "Project", "bullets": _normalize_bullets(raw)}
    return {
        "name": _first_str(raw, "name", "title", "project", "project_name", default="Project"),
        "bullets": _normalize_bullets(
            raw.get("bullets") or raw.get("responsibilities") or raw.get("description")
        ),
    }


def _normalize_education_entry(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {
            "institution": str(raw).strip() or "Institution",
            "degree": None,
            "dates": None,
            "details": None,
        }
    year = raw.get("year") or raw.get("graduation_year")
    dates = _first_str(raw, "dates", "graduation_date", "year")
    if not dates and year is not None:
        dates = str(year)
    return {
        "institution": _first_str(
            raw,
            "institution",
            "school",
            "university",
            "college",
            default="Institution",
        ),
        "degree": _first_str(raw, "degree", "qualification", "program") or None,
        "dates": dates or None,
        "details": _first_str(raw, "details", "description", "notes") or None,
    }


def _as_object_list(raw: Any) -> list[Any]:
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return raw
    return [raw]


def normalize_tailored_resume_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Map common LLM JSON shapes onto TailoredResume field names."""
    out = dict(data)
    contact = out.get("contact")
    if contact is None:
        out["contact"] = {}
    elif not isinstance(contact, dict):
        out["contact"] = {"name": str(contact)}

    experience = out.get("experience") or out.get("work_experience") or out.get("employment")
    out["experience"] = [_normalize_experience_entry(e) for e in _as_object_list(experience)]

    projects = out.get("projects") or out.get("project")
    out["projects"] = [_normalize_project_entry(p) for p in _as_object_list(projects)]

    education = out.get("education") or out.get("educations")
    out["education"] = [_normalize_education_entry(e) for e in _as_object_list(education)]

    return out
