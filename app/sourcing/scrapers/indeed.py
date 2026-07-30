"""Indeed job scraper — STUB.

NOTE: Indeed also restricts scraping and offers a publisher/API program.
Prefer official channels. Adapter shape documented below.
"""

from app.config import settings


def fetch_tech_jobs() -> list[dict]:
    if not settings.scrape_enabled:
        return []

    # TODO: implement with selectolax + httpx, respecting robots.txt and rate limits.
    return []
