from sqlalchemy import select

from app.db.models import Job
from app.sourcing import remotive, hn


def fetch_and_store(db) -> int:
    """Pull jobs from all enabled sources and persist new ones. Returns count added."""
    added = 0
    for job_dict in remotive.fetch_tech_jobs():
        added += _upsert(db, job_dict)
    for job_dict in hn.fetch_tech_jobs():
        added += _upsert(db, job_dict)
    return added


def _upsert(db, data: dict) -> int:
    exists = db.scalar(
        select(Job).where(Job.source == data["source"], Job.external_id == data["external_id"])
    )
    if exists:
        return 0
    db.add(Job(**data))
    db.commit()
    return 1
