"""Canonical tech skill + role taxonomy.

SKILL_TERMS maps lowercase aliases -> canonical skill name.
ROLE_KEYWORDS maps each TechRole to signals used for tech-role filtering.
Extend these as the project grows.
"""

import re

from app.db.models import TechRole

SKILL_TERMS: dict[str, str] = {
    # languages
    "python": "Python", "py": "Python",
    "javascript": "JavaScript", "typescript": "TypeScript",
    "java ": "Java", "golang": "Go", "go ": "Go",
    "c++": "C++", "c#": "C#", "rust": "Rust", "ruby": "Ruby",
    # backend / data
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
    "node": "Node.js", "express": "Express",
    "sql": "SQL", "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "mysql": "MySQL", "redis": "Redis", "mongodb": "MongoDB",
    # data / ml / ai
    "spark": "Spark", "kafka": "Kafka", "airflow": "Airflow", "dbt": "dbt",
    "pandas": "pandas", "numpy": "NumPy", "scikit-learn": "scikit-learn",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    "nlp": "NLP", "llm": "LLM", "rag": "RAG",
    "langchain": "LangChain", "hugging face": "Hugging Face",
    # cloud / devops
    "aws": "AWS", "gcp": "GCP", "azure": "Azure",
    "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "terraform": "Terraform", "ci/cd": "CI/CD", "jenkins": "Jenkins",
    # frontend
    "react": "React", "vue": "Vue", "angular": "Angular", "next.js": "Next.js",
}

ROLE_KEYWORDS: dict[TechRole, list[str]] = {
    TechRole.SOFTWARE_ENGINEER: ["software engineer", "backend", "frontend", "full stack", "full-stack"],
    TechRole.DATA_ENGINEER: ["data engineer", "data pipeline", "etl"],
    TechRole.DATA_SCIENTIST: ["data scientist", "machine learning", "statistic"],
    TechRole.ML_ENGINEER: ["ml engineer", "machine learning engineer", "model deployment"],
    TechRole.AI_LLM_ENGINEER: ["ai engineer", "llm engineer", "generative ai", "genai"],
    TechRole.DEVOPS_SRE: ["devops", "sre", "site reliability", "platform engineer"],
    TechRole.CLOUD_ENGINEER: ["cloud engineer", "cloud architect", "aws engineer"],
    TechRole.SECURITY_ENGINEER: ["security engineer", "appsec", "devsecops"],
    TechRole.MOBILE_ENGINEER: ["ios", "android", "react native", "flutter", "mobile engineer"],
    TechRole.QA_AUTOMATION: ["qa", "test automation", "sdet", "quality engineer"],
}

ALL_TECH_ROLES = set(ROLE_KEYWORDS.keys())

_NOISE_ALIASES = {"py"}  # short aliases prone to false positives

# Stripped alias -> canonical, used to build one boundary-aware regex so that
# e.g. "go" doesn't match "logo" and "java" doesn't match "javascript".
_STRIPPED: dict[str, str] = {
    a.strip(): c for a, c in SKILL_TERMS.items() if a.strip() and a.strip() not in _NOISE_ALIASES
}
_SKILL_RE = re.compile(
    r"(?<![a-z0-9])(" + "|".join(re.escape(a) for a in sorted(_STRIPPED, key=len, reverse=True)) + r")(?![a-z0-9])"
)


def extract_skills(text: str, limit: int = 12) -> list[str]:
    """Detect canonical skills mentioned in `text`, with word-boundary matching."""
    seen: set[str] = set()
    out: list[str] = []
    for m in _SKILL_RE.finditer((text or "").lower()):
        canonical = _STRIPPED.get(m.group(1))
        if not canonical or canonical.lower() in seen:
            continue
        seen.add(canonical.lower())
        out.append(canonical)
        if len(out) >= limit:
            break
    return out


def is_tech_text(title: str, description: str = "") -> bool:
    title_l = (title or "").lower()
    if any(any(kw in title_l for kw in kws) for kws in ROLE_KEYWORDS.values()):
        return True
    desc_l = (description or "").lower()
    hits = sum(any(kw in desc_l for kw in kws) for kws in ROLE_KEYWORDS.values())
    return hits >= 2
