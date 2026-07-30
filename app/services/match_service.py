from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job, Match, Resume
from app.matching.scorer import score_candidates
from app.schemas.match import MatchOut


def match_resume(db: Session, resume: Resume, top_n: int = 50) -> list[MatchOut]:
    jobs: list[Job] = list(db.scalars(select(Job)).all())

    scored = score_candidates(resume, jobs)            # hybrid scoring
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
