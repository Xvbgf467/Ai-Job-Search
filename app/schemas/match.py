from pydantic import BaseModel

from app.schemas.job import JobOut


class MatchOut(BaseModel):
    score: float
    keyword_score: float
    embedding_score: float
    llm_score: float | None = None
    rationale: str | None = None
    job: JobOut

    class Config:
        from_attributes = True
