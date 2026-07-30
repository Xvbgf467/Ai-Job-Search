import httpx

from app.config import settings
from app.matching.taxonomy import is_tech_text

"""Adzuna — free-tier official job API. Requires ADZUNA_APP_ID + ADZUNA_API_KEY."""

BASE = "https://api.adzuna.com/v1/api/jobs"


def fetch_tech_jobs(country: str = "us", what: str = "software engineer", results: int = 50) -> list[dict]:
    if not (settings.adzuna_app_id and settings.adzuna_api_key):
        return []  # disabled until keys are configured

    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_api_key,
        "what": what,
        "results_per_page": min(results, 50),
        "content-type": "application/json",
    }
    resp = httpx.get(f"{BASE}/{country}/search/1", params=params, timeout=30)
    resp.raise_for_status()

    out: list[dict] = []
    for j in resp.json().get("results", []):
        if not is_tech_text(j.get("title", ""), j.get("description", "")):
            continue
        out.append(
            {
                "source": "adzuna",
                "external_id": str(j.get("id")),
                "title": j.get("title", "").strip(),
                "company": j.get("company", {}).get("display_name") if isinstance(j.get("company"), dict) else j.get("company"),
                "location": j.get("location", {}).get("display_name") if isinstance(j.get("location"), dict) else j.get("location"),
                "remote": False,
                "url": j.get("redirect_url"),
                "description": j.get("description", "")[:5000],
            }
        )
    return out
