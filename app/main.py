from pathlib import Path
import threading

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select

from app.config import BASE_DIR, settings
from app.db.models import Job
from app.db.session import SessionLocal, init_db
from app.routers import api, pages
from app.services import job_service

app = FastAPI(title="TechMatch", version="0.1.0")

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(pages.router)
app.include_router(api.router, prefix="/api")


def _seed_jobs_if_empty() -> None:
    try:
        db = SessionLocal()
        try:
            if (db.scalar(select(func.count()).select_from(Job)) or 0) == 0:
                job_service.fetch_and_store(db)
        finally:
            db.close()
    except Exception:
        pass


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    threading.Thread(target=_seed_jobs_if_empty, daemon=True).start()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env, "llm": str(settings.llm_enabled)}
