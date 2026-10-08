from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

EXPORT_COLUMNS = [
    "scraped_at",
    "match_score",
    "title",
    "companyName",
    "location",
    "experienceLevel",
    "workType",
    "contractType",
    "publishedAt",
    "postedTime",
    "applicationsCount",
    "applyType",
    "applyUrl",
    "jobUrl",
    "id",
    "description",
]


def _normalize_row(job: dict[str, Any], scraped_at: str) -> dict[str, Any]:
    row = {col: job.get(col) for col in EXPORT_COLUMNS if col != "scraped_at"}
    row["scraped_at"] = scraped_at
    row["match_score"] = job.get("match_score")
    if row.get("id") is None:
        row["id"] = job.get("jobId") or job.get("job_id")
    desc = row.get("description")
    if isinstance(desc, str) and len(desc) > 32000:
        row["description"] = desc[:32000] + "…"
    return row


def append_to_excel(
    jobs: list[dict[str, Any]],
    excel_path: Path,
    sheet_name: str,
) -> tuple[int, int]:
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    scraped_at = datetime.now(timezone.utc).isoformat()
    new_rows = [_normalize_row(job, scraped_at) for job in jobs]
    new_df = pd.DataFrame(new_rows, columns=EXPORT_COLUMNS)

    if excel_path.is_file():
        existing = pd.read_excel(excel_path, sheet_name=sheet_name)
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df

    if "id" in combined.columns:
        combined["id"] = combined["id"].astype(str)
        combined = combined.drop_duplicates(subset=["id"], keep="last")

    combined = combined.sort_values(
        by=["scraped_at", "match_score"],
        ascending=[False, False],
        na_position="last",
    )

    added = len(new_df)
    total = len(combined)
    _write_workbook(combined, excel_path, sheet_name)
    return added, total


def _write_workbook(combined: pd.DataFrame, excel_path: Path, sheet_name: str) -> None:
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = excel_path.with_suffix(".tmp.xlsx")
    try:
        with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
            combined.to_excel(writer, sheet_name=sheet_name, index=False)
        tmp_path.replace(excel_path)
    except PermissionError:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        fallback = excel_path.with_name(f"{excel_path.stem}_{stamp}.xlsx")
        with pd.ExcelWriter(fallback, engine="openpyxl") as writer:
            combined.to_excel(writer, sheet_name=sheet_name, index=False)
        if tmp_path.is_file():
            tmp_path.unlink(missing_ok=True)
        raise PermissionError(
            f"Could not write '{excel_path}' — close the file in Excel (or another app) and retry. "
            f"Saved this run to '{fallback}' instead."
        ) from None
    finally:
        if tmp_path.is_file() and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
