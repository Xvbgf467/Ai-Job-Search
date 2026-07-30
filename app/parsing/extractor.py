from dataclasses import dataclass, field

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


def _guess_years(text: str) -> int | None:
    import re

    m = re.search(r"(\d{1,2})\+?\s*years?\s+(?:of\s+)?(?:experience|exp)", text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def _guess_location(text: str) -> str | None:
    import re

    for line in text.splitlines():
        if re.search(r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b", line):
            return line.strip()
    return None
