from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.db.models import Resume, TechRole
from app.parsing.document import load_text
from app.parsing.extractor import extract_profile


class UnsupportedFormat(Exception):
    pass


_ALLOWED = {".pdf", ".docx", ".txt"}


async def ingest_upload(
    db: Session,
    *,
    name: str,
    target_role: str | None,
    file: UploadFile,
    years_experience: int | None = None,
) -> Resume:
    suffix = "." + (file.filename or "").rsplit(".", 1)[-1].lower()
    if suffix not in _ALLOWED:
        raise UnsupportedFormat(f"Unsupported file type: {suffix}. Use one of {sorted(_ALLOWED)}")

    data = await file.read()
    text = load_text(suffix, data)
    profile = extract_profile(text)

    resume = Resume(
        name=name,
        raw_text=text,
        target_role=TechRole(target_role) if target_role else profile.target_role,
        skills=",".join(profile.skills),
        years_experience=years_experience if years_experience is not None else profile.years_experience,
        location=profile.location,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def get(db: Session, resume_id: int) -> Resume | None:
    return db.get(Resume, resume_id)
