import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TechRole(str, enum.Enum):
    SOFTWARE_ENGINEER = "software_engineer"
    DATA_ENGINEER = "data_engineer"
    DATA_SCIENTIST = "data_scientist"
    ML_ENGINEER = "ml_engineer"
    AI_LLM_ENGINEER = "ai_llm_engineer"
    DEVOPS_SRE = "devops_sre"
    CLOUD_ENGINEER = "cloud_engineer"
    SECURITY_ENGINEER = "security_engineer"
    MOBILE_ENGINEER = "mobile_engineer"
    QA_AUTOMATION = "qa_automation"


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    raw_text: Mapped[str] = mapped_column(Text)
    target_role: Mapped[TechRole | None] = mapped_column(Enum(TechRole), nullable=True)
    skills: Mapped[str] = mapped_column(Text, default="")          # comma-separated
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    matches: Mapped[list["Match"]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(50))                # adzuna | remotive | linkedin ...
    external_id: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(512))
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remote: Mapped[bool] = mapped_column(default=False)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    role: Mapped[TechRole | None] = mapped_column(Enum(TechRole), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    score: Mapped[float] = mapped_column(Float)                    # 0.0 - 1.0 composite
    keyword_score: Mapped[float] = mapped_column(Float, default=0.0)
    embedding_score: Mapped[float] = mapped_column(Float, default=0.0)
    llm_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)   # "why it matched"

    resume: Mapped["Resume"] = relationship(back_populates="matches")
    job: Mapped["Job"] = relationship()
