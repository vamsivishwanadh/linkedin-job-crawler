from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def _parse_iso(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    try:
        if len(text) == 10:
            return datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def job_posted_at(job: dict[str, Any]) -> datetime | None:
    ts = job.get("postedAtTimestamp")
    if isinstance(ts, (int, float)) and ts > 0:
        return datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)

    for key in ("publishedAt", "postedTime"):
        raw = job.get(key)
        if isinstance(raw, str):
            parsed = _parse_iso(raw)
            if parsed:
                return parsed
    return None


def is_within_hours(job: dict[str, Any], min_hours: float, max_hours: float) -> bool:
    posted = job_posted_at(job)
    if posted is None:
        # Apify already filtered by publishedAt; keep if we cannot parse time.
        return True

    now = datetime.now(timezone.utc)
    age = now - posted
    lower = timedelta(hours=min_hours)
    upper = timedelta(hours=max_hours)
    return lower <= age <= upper
