import httpx

from app.matching.taxonomy import is_tech_text

BASE = "https://remotive.com/api/remote-jobs"


def fetch_tech_jobs() -> list[dict]:
    """Remotive has a free, keyless API with good tech coverage."""
    resp = httpx.get(BASE, timeout=30)
    resp.raise_for_status()
    jobs = resp.json().get("jobs", [])

    out: list[dict] = []
    for j in jobs:
        if not is_tech_text(f"{j.get('title','')} {j.get('description','')}"):
            continue
        out.append(
            {
                "source": "remotive",
                "external_id": str(j.get("id")),
                "title": j.get("title", "").strip(),
                "company": j.get("company_name"),
                "location": j.get("candidate_required_location"),
                "remote": True,
                "url": j.get("url"),
                "description": j.get("description", "")[:5000],
            }
        )
    return out
