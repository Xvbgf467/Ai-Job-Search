"""Canonical tech skill + role taxonomy.

SKILL_TERMS maps lowercase aliases -> canonical skill name.
ROLE_KEYWORDS maps each TechRole to signals used for tech-role filtering.
Extend these as the project grows.
"""

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


def is_tech_text(text: str) -> bool:
    lowered = text.lower()
    return any(any(kw in lowered for kw in kws) for kws in ROLE_KEYWORDS.values())
