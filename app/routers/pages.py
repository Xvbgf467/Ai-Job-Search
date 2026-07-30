from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.db.models import Job, TechRole
from app.db.session import SessionLocal, get_db
from app.matching import seniority, taxonomy
from app.services import match_service, resume_service

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _job_count() -> int:
    db = SessionLocal()
    try:
        return int(db.scalar(select(func.count()).select_from(Job)) or 0)
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"roles": [r.value for r in TechRole], "job_count": _job_count()},
    )


@router.get("/resume", response_class=HTMLResponse)
def resume_page(request: Request):
    return templates.TemplateResponse(
        request,
        "resume.html",
        {"roles": [r.value for r in TechRole], "job_count": _job_count()},
    )


@router.post("/match", response_class=HTMLResponse)
async def match(
    request: Request,
    name: str = Form(...),
    target_role: str | None = Form(None),
    years_experience: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        resume = await resume_service.ingest_upload(
            db,
            name=name,
            target_role=target_role,
            file=file,
            years_experience=years_experience,
        )
    except resume_service.UnsupportedFormat as exc:
        return templates.TemplateResponse(request, "error.html", {"message": str(exc)})

    candidate_level = seniority.years_to_level(resume.years_experience)

    # Offload the CPU/LLM-heavy matching to a worker thread (own session) so the
    # event loop stays responsive. Build an enriched result with skill gaps.
    resume_id = resume.id

    def _run_match() -> list[dict]:
        session = SessionLocal()
        try:
            fresh = resume_service.get(session, resume_id)
            matches = match_service.match_resume(session, fresh)
            resume_skills = {s.strip().lower() for s in (fresh.skills or "").split(",") if s.strip()}
            enriched: list[dict] = []
            for m in matches:
                job = session.get(Job, m.job.id)
                job_skills = taxonomy.extract_skills(f"{job.title} {job.description}")
                enriched.append(
                    {
                        "score": m.score,
                        "keyword_score": m.keyword_score,
                        "embedding_score": m.embedding_score,
                        "llm_score": m.llm_score,
                        "rationale": m.rationale,
                        "job": job,
                        "seniority": seniority.detect_seniority(job.title),
                        "matched": [s for s in job_skills if s.lower() in resume_skills],
                        "missing": [s for s in job_skills if s.lower() not in resume_skills],
                    }
                )
            return enriched
        finally:
            session.close()

    results = await run_in_threadpool(_run_match)
    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "resume": resume,
            "results": results,
            "candidate_level": candidate_level,
            "years": resume.years_experience,
        },
    )
