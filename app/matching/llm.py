"""LLM re-ranker for the top-N candidates.

Uses an OpenAI-compatible client (Z.AI / GLM by default). Maps each job to a
short numeric id for the prompt, then maps scores+rationales back onto the
original job dicts. Returns input unchanged when LLM is disabled.
"""

import json
import re

from openai import OpenAI

from app.config import settings

_SYSTEM = (
    "You are a senior tech recruiter. Given a candidate's resume and a list of "
    "tech job postings, rate how well each job fits the candidate from 0.0 to 1.0 "
    "and give a rationale of at most 8 words. Respond ONLY with compact JSON."
)

_USER_TMPL = """CANDIDATE RESUME:
{resume}

JOBS (id | title | description):
{jobs}

Return JSON shaped exactly like:
{{"results":[{{"id":1,"score":0.82,"rationale":"short reason"}}]}}

Rate every job id listed. score in [0,1]."""


def _client() -> OpenAI:
    return OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url or None,
        timeout=settings.llm_timeout,
        max_retries=1,
    )


def _parse_results(text: str) -> list[dict]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return []
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []


def rerank(resume_text: str, jobs: list[dict]) -> list[dict]:
    """Re-score `jobs` (each: job_id, title, description, score) with the LLM.

    Adds `llm_score` and `rationale` to each job and re-sorts by llm_score.
    """
    if not settings.llm_enabled or not jobs:
        return jobs

    # stable 1..N ids to avoid JSON type drift, map back at the end
    indexed = list(enumerate(jobs, start=1))
    jobs_block = "\n".join(
        f"{i} | {j.get('title','')[:120]} | {(j.get('description','') or '')[:240]}"
        for i, j in indexed
    )

    try:
        resp = _client().chat.completions.create(
            model=settings.llm_model,
            temperature=0.2,
            max_tokens=2048,
            extra_body={"thinking": {"type": "disabled"}},
            messages=[
                {"role": "system", "content": _SYSTEM},
                {
                    "role": "user",
                    "content": _USER_TMPL.format(
                        resume=resume_text[:2000], jobs=jobs_block
                    ),
                },
            ],
        )
    except Exception:
        return jobs  # never break the pipeline on an LLM error

    content = resp.choices[0].message.content or ""
    scored = {int(r["id"]): r for r in _parse_results(content) if "id" in r}

    for i, job in indexed:
        r = scored.get(i)
        if not r:
            continue
        try:
            job["llm_score"] = max(0.0, min(1.0, float(r.get("score", 0.0))))
        except (TypeError, ValueError):
            continue
        job["rationale"] = str(r.get("rationale", ""))[:300]

    return sorted(
        jobs,
        key=lambda j: j.get("llm_score") if j.get("llm_score") is not None else -1,
        reverse=True,
    )
