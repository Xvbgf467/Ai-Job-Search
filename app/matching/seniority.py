"""Seniority / experience-level helpers.

Maps years of experience to a coarse level and detects a job's seniority from
its title, so matching can favour level-appropriate roles.
"""

import re

LEVELS = ["intern", "junior", "mid", "senior", "lead"]


def years_to_level(years: int | None) -> str | None:
    if years is None:
        return None
    if years <= 0:
        return "intern"
    if years <= 2:
        return "junior"
    if years <= 5:
        return "mid"
    if years <= 8:
        return "senior"
    return "lead"


_SENIORITY_PATTERNS = [
    ("intern", re.compile(r"\b(intern(?:ship)?|apprentice|entry[\s-]?level)\b", re.I)),
    ("junior", re.compile(r"\b(junior|jr\.?|associate|graduate)\b", re.I)),
    ("senior", re.compile(r"\b(senior|sr\.?|lead|staff|principal)\b", re.I)),
]


def detect_seniority(title: str) -> str:
    """Job seniority from its title; defaults to 'mid' when there's no signal."""
    for level, pat in _SENIORITY_PATTERNS:
        if pat.search(title or ""):
            return level
    return "mid"


def _distance(a: str | None, b: str) -> int:
    if a is None:
        return 0
    ia = LEVELS.index(a) if a in LEVELS else 2
    ib = LEVELS.index(b) if b in LEVELS else 2
    return abs(ia - ib)


_FACTOR_BY_DISTANCE = {0: 1.0, 1: 0.95, 2: 0.88, 3: 0.80, 4: 0.72}


def level_factor(candidate_level: str | None, job_title: str) -> float:
    """Score multiplier in ~[0.7, 1.0]; closer seniority ranks higher."""
    if candidate_level is None:
        return 1.0
    return _FACTOR_BY_DISTANCE.get(_distance(candidate_level, detect_seniority(job_title)), 0.7)
