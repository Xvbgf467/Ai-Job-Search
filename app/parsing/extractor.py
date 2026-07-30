from dataclasses import dataclass, field
import re
from datetime import datetime

from app.db.models import TechRole
from app.matching.taxonomy import SKILL_TERMS, ROLE_KEYWORDS


@dataclass
class Profile:
    skills: list[str] = field(default_factory=list)
    target_role: TechRole | None = None
    years_experience: int | None = None
    location: str | None = None


def extract_profile(text: str) -> Profile:
    """Rule-based first pass. Swap for an LLM extractor later for richer detail."""
    lowered = text.lower()

    skills = sorted({canon for term, canon in SKILL_TERMS.items() if term in lowered})

    role_scores: dict[TechRole, int] = {}
    for role, kws in ROLE_KEYWORDS.items():
        role_scores[role] = sum(1 for kw in kws if kw in lowered)
    target_role = max(role_scores, key=role_scores.get) if any(role_scores.values()) else None

    years = _guess_years(text)
    location = _guess_location(text)

    return Profile(skills=skills, target_role=target_role, years_experience=years, location=location)


_YEARS_PATTERNS = [
    r"(\d{1,2})\+\s*years?",
    r"(\d{1,2})\s*years?\s*(?:of\s+)?(?:experience|exp|professional)",
    r"over\s+(\d{1,2})\s*years?",
]
_RANGE_START_RE = re.compile(r"(?:(?:since|from)\s+)?((?:19|20)\d{2})\s*(?:–|-|—|to)", re.IGNORECASE)


def _guess_years(text: str) -> int | None:
    for pat in _YEARS_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 0 < val < 50:
                return val
    starts = [int(y) for y in _RANGE_START_RE.findall(text)]
    if starts:
        est = datetime.now().year - min(starts)
        if 0 <= est <= 45:
            return est
    return None


_LOC_RE = re.compile(r"\b([A-Z][\w.\-']+(?:\s+[A-Z][\w.\-']+)?,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z]{2,}))\b")
_LOC_SKIP = ("skill", "methodolog", "technolog", "stack", "tool", "framework", "language")


def _guess_location(text: str) -> str | None:
    for line in text.splitlines():
        if re.search(r"@|\+\d|linkedin|github", line, re.IGNORECASE):
            m = _LOC_RE.search(line)
            if m:
                return m.group(1)
    for line in text.splitlines():
        s = line.strip()
        if not s or len(s) > 60 or ":" in s or s.count(",") > 2:
            continue
        if any(k in s.lower() for k in _LOC_SKIP):
            continue
        m = _LOC_RE.search(s)
        if m:
            return m.group(1)
    return None
