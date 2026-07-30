from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.db.models import Resume


def keyword_score(resume: Resume, job_text: str) -> float:
    """TF-IDF cosine similarity between resume text and job text, in [0, 1]."""
    docs = [resume.raw_text, job_text]
    try:
        tfidf = TfidfVectorizer(stop_words="english").fit_transform(docs)
    except ValueError:
        return 0.0
    sim = cosine_similarity(tfidf[0], tfidf[1])[0, 0]
    return float(max(0.0, min(1.0, sim)))


def skill_overlap(resume: Resume, job_text: str) -> float:
    """Jaccard-ish overlap of resume skills found in the job text."""
    skills = [s for s in (resume.skills or "").split(",") if s]
    if not skills:
        return 0.0
    lowered = job_text.lower()
    hits = sum(1 for s in skills if s.lower() in lowered)
    return hits / len(skills)
