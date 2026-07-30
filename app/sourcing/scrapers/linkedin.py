"""LinkedIn job scraper — STUB.

WARNING: Scraping LinkedIn generally violates their Terms of Service and they
actively block automated access. Prefer the official LinkedIn Jobs API or a
licensed data provider (Bright Data, SerpApi) instead. This stub exists to
document the adapter shape, not to encourage ToS violations.
"""

from app.config import settings


def fetch_tech_jobs() -> list[dict]:
    if not settings.scrape_enabled:
        return []

    # TODO: implement via a licensed API/SerpApi, or a headless browser with
    # rate limiting, proxies, and robots.txt compliance. Left intentionally empty.
    return []
