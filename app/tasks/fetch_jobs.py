"""Scheduled background job that refreshes the job pool.

Run via APScheduler in a worker process, or call refresh() manually.
"""

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services import job_service

scheduler = BackgroundScheduler()


def refresh() -> int:
    db = SessionLocal()
    try:
        return job_service.fetch_and_store(db)
    finally:
        db.close()


def start(every_hours: int = 6) -> None:
    scheduler.add_job(refresh, "interval", hours=every_hours, id="fetch_jobs")
    scheduler.start()
