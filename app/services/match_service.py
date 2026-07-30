from types import SimpleNamespace

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job, Match, Resume
from app.matching import embeddings, keywords, llm, seniority, taxonomy
from app.matching.scorer import WEIGHTS, _desired_factor, score_candidates
from app.schemas.match import MatchOut


def match_resume(
    db: Session,
    resume: Resume,
    top_n: int = 50,
    *,
    region: str | None = None,
    desired_skills: list[str] | None = None,
) -> list[MatchOut]:
    jobs: list[Job] = list(db.scalars(select(Job)).all())

    scored = score_candidates(
        resume, jobs, region=region, desired_skills=desired_skills
    )  # hybrid scoring
    scored.sort(key=lambda m: m["score"], reverse=True)
    scored = scored[:top_n]

    # replace existing matches for this resume
    db.query(Match).filter(Match.resume_id == resume.id).delete()

    results: list[MatchOut] = []
    for m in scored:
        match = Match(
            resume_id=resume.id,
            job_id=m["job_id"],
            score=m["score"],
            keyword_score=m["keyword_score"],
            embedding_score=m["embedding_score"],
            llm_score=m.get("llm_score"),
            rationale=m.get("rationale"),
        )
        db.add(match)
        results.append(_to_out(db, match, m["job_id"]))
    db.commit()
    return results


def _to_out(db: Session, match: Match, job_id: int) -> MatchOut:
    job = db.get(Job, job_id)
    return MatchOut(
        score=match.score,
        keyword_score=match.keyword_score,
        embedding_score=match.embedding_score,
        llm_score=match.llm_score,
        rationale=match.rationale,
        job=job,
    )


def match_job_description(
    resume: Resume,
    title: str | None,
    description: str,
    *,
    region: str | None = None,
    desired_skills: list[str] | None = None,
) -> dict:
    """Score the resume against a single pasted job description (not in the pool)."""
    title = (title or "Pasted job description").strip() or "Pasted job description"
    description = (description or "").strip()
    text = f"{title}\n{description}"

    kw = 0.5 * keywords.keyword_score(resume, text) + 0.5 * keywords.skill_overlap(resume, text)
    emb = embeddings.similarity(embeddings.embed(resume.raw_text), embeddings.embed(text))

    cand_level = seniority.years_to_level(resume.years_experience)
    factor = seniority.level_factor(cand_level, title) * _desired_factor(desired_skills, text.lower())

    reranked = llm.rerank(
        resume.raw_text, [{"job_id": 1, "title": title, "description": description, "score": 0.0}]
    )
    llm_score = reranked[0].get("llm_score") if reranked else None
    rationale = reranked[0].get("rationale") if reranked else None

    base = WEIGHTS["keyword"] * kw + WEIGHTS["embedding"] * emb
    score = (base + WEIGHTS["llm"] * llm_score) * factor if llm_score is not None else base * factor

    resume_skills = {s.strip().lower() for s in (resume.skills or "").split(",") if s.strip()}
    job_skills = taxonomy.extract_skills(text)
    job = SimpleNamespace(
        source="pasted",
        title=title,
        description=description,
        company=None,
        location=None,
        remote=False,
        url=None,
        posted_at=None,
    )
    return {
        "score": score,
        "keyword_score": kw,
        "embedding_score": emb,
        "llm_score": llm_score,
        "rationale": rationale,
        "job": job,
        "seniority": seniority.detect_seniority(title),
        "matched": [s for s in job_skills if s.lower() in resume_skills],
        "missing": [s for s in job_skills if s.lower() not in resume_skills],
    }
