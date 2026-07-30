from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.match import MatchOut
from app.schemas.resume import ResumeOut
from app.services import match_service, resume_service

router = APIRouter()


@router.post("/resumes/upload", response_model=ResumeOut)
async def upload_resume(
    name: str = Form(...),
    target_role: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        resume = await resume_service.ingest_upload(db, name=name, target_role=target_role, file=file)
    except resume_service.UnsupportedFormat as exc:
        raise HTTPException(status_code=415, detail=str(exc))
    return resume


@router.post("/resumes/{resume_id}/match", response_model=list[MatchOut])
def match_jobs(resume_id: int, db: Session = Depends(get_db)):
    resume = resume_service.get(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="resume not found")
    return match_service.match_resume(db, resume)
