from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.db.models import TechRole
from app.db.session import get_db
from app.services import match_service, resume_service

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"roles": [r.value for r in TechRole]},
    )


@router.get("/resume", response_class=HTMLResponse)
def resume_page(request: Request):
    return templates.TemplateResponse(
        request, "resume.html", {"roles": [r.value for r in TechRole]}
    )


@router.post("/match", response_class=HTMLResponse)
async def match(
    request: Request,
    name: str = Form(...),
    target_role: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        resume = await resume_service.ingest_upload(
            db, name=name, target_role=target_role, file=file
        )
    except resume_service.UnsupportedFormat as exc:
        return templates.TemplateResponse(request, "error.html", {"message": str(exc)})

    matches = match_service.match_resume(db, resume)
    return templates.TemplateResponse(
        request, "results.html", {"resume": resume, "matches": matches}
    )
