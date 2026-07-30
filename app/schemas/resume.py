from datetime import datetime

from pydantic import BaseModel, field_validator

from app.db.models import TechRole


class ResumeBase(BaseModel):
    name: str
    target_role: TechRole | None = None
    skills: list[str] = []
    years_experience: int | None = None
    location: str | None = None

    @field_validator("skills", mode="before")
    @classmethod
    def _split_skills(cls, v):
        if isinstance(v, str):
            return [s for s in v.split(",") if s.strip()]
        return v


class ResumeCreate(ResumeBase):
    raw_text: str


class ResumeOut(ResumeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
