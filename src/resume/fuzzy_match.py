from __future__ import annotations

import re
from difflib import SequenceMatcher

_WHITESPACE = re.compile(r"\s+")
_WORD = re.compile(r"[a-z0-9][a-z0-9+#./-]*", re.IGNORECASE)


def normalize_text(text: str) -> str:
    return _WHITESPACE.sub(" ", text.lower().strip())


def skill_match_confidence(skill: str, master_resume: str) -> tuple[float, str | None]:
    """
    Return (confidence 0–1, matched snippet from resume if any).
    1.0 = exact substring in normalized resume.
    """
    skill_n = normalize_text(skill)
    if len(skill_n) < 2:
        return 1.0, skill_n

    body_n = normalize_text(master_resume)
    if skill_n in body_n:
        return 1.0, skill_n

    best_ratio = 0.0
    best_span: str | None = None

    words = _WORD.findall(body_n)
    for word in words:
        if len(word) < 2:
            continue
        ratio = SequenceMatcher(None, skill_n, word).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_span = word

    skill_parts = skill_n.split()
    if len(skill_parts) > 1:
        phrase = " ".join(skill_parts)
        if phrase in body_n:
            return 1.0, phrase
        for i in range(len(words) - len(skill_parts) + 1):
            window = " ".join(words[i : i + len(skill_parts)])
            ratio = SequenceMatcher(None, phrase, window).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_span = window

    if best_ratio >= 0.99:
        return 1.0, best_span
    return best_ratio, best_span
