"""Command-line resume -> tech job matcher.

Usage:
    python scripts/match.py path/to/resume.pdf --name "Jane Doe" --top 10
    python scripts/match.py cv.docx --role ai_llm_engineer --fetch
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.models import Resume, TechRole
from app.db.session import SessionLocal
from app.parsing.document import load_text
from app.parsing.extractor import extract_profile
from app.services import job_service, match_service


def main() -> None:
    ap = argparse.ArgumentParser(description="Match a resume against tech jobs.")
    ap.add_argument("resume", help="path to resume file (pdf/docx/txt)")
    ap.add_argument("--name", default="Candidate", help="candidate name")
    ap.add_argument("--role", default=None, help="target role enum value (e.g. software_engineer)")
    ap.add_argument("--top", type=int, default=10, help="number of results to print")
    ap.add_argument("--fetch", action="store_true", help="refresh the job pool before matching")
    args = ap.parse_args()

    suffix = "." + args.resume.rsplit(".", 1)[-1].lower()
    try:
        text = load_text(suffix, open(args.resume, "rb").read())
    except Exception as exc:
        print(f"could not read resume: {exc}", file=sys.stderr)
        sys.exit(1)

    profile = extract_profile(text)

    db = SessionLocal()
    try:
        if args.fetch:
            print("fetching fresh jobs...")
            print(f"  +{job_service.fetch_and_store(db)} new jobs")

        resume = Resume(
            name=args.name,
            raw_text=text,
            target_role=TechRole(args.role) if args.role else profile.target_role,
            skills=",".join(profile.skills),
            years_experience=profile.years_experience,
            location=profile.location,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        matches = match_service.match_resume(db, resume)

        print(f"\n{resume.name} | {profile.target_role.value if profile.target_role else '?'}"
              f" | {profile.location or '?'} | ~{profile.years_experience or '?'} yrs")
        print(f"skills: {', '.join(profile.skills)}\n")
        print(f"{len(matches)} matched tech jobs (showing top {min(args.top, len(matches))}):\n")
        for m in matches[: args.top]:
            j = m.job
            ll = f"/{m.llm_score:.2f}" if m.llm_score is not None else ""
            print(f"  {m.score * 100:4.0f}% [{m.keyword_score:.2f}/{m.embedding_score:.2f}{ll}]"
                  f"  {j.title[:72]}")
            meta = " | ".join(x for x in (j.company, j.location, j.source) if x)
            if meta:
                print(f"        {meta}")
            if m.rationale:
                print(f"        -> {m.rationale}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
