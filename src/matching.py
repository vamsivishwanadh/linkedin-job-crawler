from __future__ import annotations

from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_resume_text(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(
            f"Resume not found at {path}. Copy resume/resume.example.txt to resume/resume.txt "
            "and paste your resume."
        )
    return path.read_text(encoding="utf-8").strip()


def score_jobs_against_resume(jobs: list[dict[str, Any]], resume_text: str) -> list[float]:
    if not jobs:
        return []

    job_docs = []
    for job in jobs:
        title = str(job.get("title") or "")
        company = str(job.get("companyName") or "")
        desc = str(job.get("description") or "")
        job_docs.append(f"{title} {company} {desc}")

    corpus = [resume_text, *job_docs]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=8000)
    matrix = vectorizer.fit_transform(corpus)
    resume_vec = matrix[0:1]
    job_matrix = matrix[1:]
    similarities = cosine_similarity(resume_vec, job_matrix)[0]
    return [float(x) for x in similarities]


def attach_match_scores(jobs: list[dict[str, Any]], resume_text: str) -> list[dict[str, Any]]:
    scores = score_jobs_against_resume(jobs, resume_text)
    enriched: list[dict[str, Any]] = []
    for job, score in zip(jobs, scores, strict=True):
        row = dict(job)
        row["match_score"] = round(score, 4)
        enriched.append(row)
    return enriched
