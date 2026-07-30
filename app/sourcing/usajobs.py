import httpx

from app.config import settings
from app.matching.taxonomy import is_tech_text

"""USAJOBS — official US federal jobs API. Requires USAJOBS_API_KEY (free)."""

BASE = "https://data.usajobs.gov/api/search"


def fetch_tech_jobs(keyword: str = "IT Specialist", results: int = 50) -> list[dict]:
    if not settings.usajobs_api_key:
        return []

    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": settings.user_agent,
        "Authorization-Key": settings.usajobs_api_key,
    }
    params = {"Keyword": keyword, "ResultsPerPage": min(results, 500)}
    resp = httpx.get(BASE, headers=headers, params=params, timeout=30)
    resp.raise_for_status()

    out: list[dict] = []
    for item in resp.json().get("SearchResult", {}).get("SearchResultItems", []):
        j = item.get("MatchedObjectDescriptor", {})
        title = j.get("PositionTitle", "")
        if not is_tech_text(title, j.get("QualificationSummary", "")):
            continue
        out.append(
            {
                "source": "usajobs",
                "external_id": item.get("MatchedObjectId", ""),
                "title": title.strip(),
                "company": j.get("OrganizationName"),
                "location": ", ".join(
                    l.get("Name", "") for l in j.get("PositionLocation", [])
                ) or None,
                "remote": False,
                "url": j.get("PositionURI"),
                "description": j.get("QualificationSummary", "")[:5000],
            }
        )
    return out
