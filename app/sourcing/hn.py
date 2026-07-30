import httpx

"""Hacker News "Ask HN: Who is hiring?" monthly thread.

No API key, just the public Algolia HN search. Great for early-stage tech jobs.
"""

HN_SEARCH = "https://hn.algolia.com/api/v1/search"


def fetch_tech_jobs(month_tag: str = "") -> list[dict]:
    query = f'"Who is hiring" ask hn {month_tag}'.strip()
    resp = httpx.get(HN_SEARCH, params={"query": query, "tags": "story"}, timeout=30)
    resp.raise_for_status()
    hits = resp.json().get("hits", [])

    thread_id = hits[0]["objectID"] if hits else None
    if not thread_id:
        return []

    # pull top-level comments of that thread (each is a job post)
    resp = httpx.get(HN_SEARCH, params={"tags": f"comment,story_{thread_id}", "hitsPerPage": 50}, timeout=30)
    resp.raise_for_status()

    out: list[dict] = []
    for h in resp.json().get("hits", []):
        text = h.get("comment_text", "") or ""
        first_line = text.split("\n", 1)[0][:120]
        out.append(
            {
                "source": "hn",
                "external_id": h["objectID"],
                "title": first_line,
                "company": None,
                "location": None,
                "remote": None,
                "url": f"https://news.ycombinator.com/item?id={h['objectID']}",
                "description": text[:5000],
            }
        )
    return out
