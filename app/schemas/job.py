from datetime import datetime

from pydantic import BaseModel

from app.db.models import TechRole


class JobOut(BaseModel):
    id: int
    source: str
    title: str
    company: str | None = None
    location: str | None = None
    remote: bool = False
    url: str | None = None
    role: TechRole | None = None
    posted_at: datetime | None = None

    class Config:
        from_attributes = True
