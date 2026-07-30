"""Composite hybrid scorer.

Pipeline:
  1. keyword overlap (TF-IDF + skill overlap)  -> fast, free
  2. semantic embedding similarity              -> understands synonyms
  3. optional LLM re-rank of top-N               -> best accuracy, controlled cost
"""

from app.db.models import Job, Resume
from app.matching import embeddings, keywords, llm
from app.matching.taxonomy import is_tech_text
from app.config import settings

WEIGHTS = {"keyword": 0.4, "embedding": 0.4, "llm": 0.2}


def score_candidates(resume: Resume, jobs: list[Job]) -> list[dict]:
    # 1. tech-only filter: drop non-tech postings early
    tech_jobs = [j for j in jobs if is_tech_text(j.title, j.description)]
    if not tech_jobs:
        return []

    # 2. per-job keyword + embedding scores
    resume_vec = embeddings.embed(resume.raw_text)
    candidates: list[dict] = []

    for job in tech_jobs:
        job_text = f"{job.title}\n{job.description}"
        kw = 0.5 * keywords.keyword_score(resume, job_text) + 0.5 * keywords.skill_overlap(resume, job_text)
        emb = embeddings.similarity(resume_vec, embeddings.embed(job_text))
        candidates.append(
            {
                "job_id": job.id,
                "keyword_score": kw,
                "embedding_score": emb,
                "score": WEIGHTS["keyword"] * kw + WEIGHTS["embedding"] * emb,
            }
        )

    candidates.sort(key=lambda m: m["score"], reverse=True)

    # 3. optional LLM re-rank of the top slice
    top = candidates[: settings.llm_rerank_top_n]
    top = llm.rerank(
        resume.raw_text,
        [
            {
                "job_id": c["job_id"],
                "title": job.title,
                "description": job.description,
                "score": c["score"],
            }
            for c in top
            for job in [next(j for j in tech_jobs if j.id == c["job_id"])]
        ],
    )
    # merge back llm scores
    by_id = {c["job_id"]: c for c in candidates}
    for r in top:
        c = by_id.get(r["job_id"])
        if not c:
            continue
        c["llm_score"] = r.get("llm_score")
        c["rationale"] = r.get("rationale")
        if c["llm_score"] is not None:
            c["score"] = (
                WEIGHTS["keyword"] * c["keyword_score"]
                + WEIGHTS["embedding"] * c["embedding_score"]
                + WEIGHTS["llm"] * c["llm_score"]
            )

    candidates = sorted(by_id.values(), key=lambda m: m["score"], reverse=True)
    return candidates
