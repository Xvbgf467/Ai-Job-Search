# TechMatch — Tech-Only Resume → Job Matcher

A full-stack Python app that takes a person's resume and surfaces the best-matching
**tech jobs only** (Software Engineer, Data Engineer, Data Scientist/ML Engineer,
AI/LLM Engineer, DevOps/SRE, Cloud, Security, Mobile, QA/Automation).

## How it works

```
Resume (PDF/DOCX/TXT)
        │
        ▼
[1. Parsing]      extract skills, role, years of exp, location pref
        │
        ▼
[2. Sourcing]     public APIs (Adzuna, Remotive, USAJobs, HN) + scrapers
        │
        ▼
[3. Matching]     keyword/TF-IDF → embeddings → LLM re-rank (hybrid)
        │
        ▼
[4. Dashboard]    ranked jobs, match-score breakdown, "why it matched"
```

## Architecture

| Layer | Choice | Notes |
|------|--------|-------|
| Backend | **FastAPI** | async, great for AI/LLM work |
| Frontend | **Jinja2 + HTMX + Tailwind** | server-rendered, no separate JS build |
| DB | **SQLite** (dev) / **Postgres** (prod) | via SQLAlchemy + Alembic |
| Vector store | **FAISS** (dev) / **pgvector** (prod) | for embedding similarity |
| Embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | local, free |
| LLM re-rank | OpenAI/Anthropic (optional) | top-N only, to control cost |
| Background jobs | **APScheduler** or **RQ** | periodic job fetching |
| Packaging | **uv** + `pyproject.toml` | |

## Folder layout

```
techmatch/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # pydantic-settings
│   ├── db/                  # SQLAlchemy models, session
│   ├── schemas/             # pydantic DTOs (resume, job, match)
│   ├── parsing/             # resume loaders + skill extractor
│   ├── sourcing/            # job sources (adapter pattern)
│   │   ├── base.py          #   JobSource interface
│   │   ├── adzuna/remotive/usajobs/hn.py
│   │   └── scrapers/        # linkedin, indeed
│   ├── matching/            # keywords, embeddings, llm, scorer, taxonomy
│   ├── vectorstore/         # FAISS wrapper
│   ├── services/            # business logic orchestration
│   ├── routers/             # pages (HTMX) + JSON API
│   ├── tasks/               # scheduled job fetchers
│   ├── templates/           # Jinja2
│   └── static/              # css/js (Tailwind)
└── tests/
```

## Matching pipeline (hybrid)

1. **Keyword / TF-IDF** — fast hard filter on skill overlap; cheap, no cost.
2. **Semantic embeddings** — cosine similarity between resume vector and job vector;
   understands "React" ≈ "frontend".
3. **LLM re-rank** — top ~20 candidates scored by an LLM with a fit rationale
   (only top-N to limit token cost).

Final score = weighted blend. Filters: location, remote, salary, seniority, stack.

## Tech-role whitelist

Matching only keeps jobs classified as tech roles; non-tech postings are dropped
at the sourcing/normalization step.

## Status

Scaffolding complete. Implementation order:

- [ ] Resume parsing (PDF/DOCX/TXT → structured profile)
- [ ] Skill/role taxonomy
- [ ] Sourcing adapters (start with Remotive + HN — no key / open)
- [ ] Keyword + embedding scorer
- [ ] LLM re-rank
- [ ] Dashboard UI + filters
- [ ] Background fetcher + persistence
- [ ] Scrapers (LinkedIn/Indeed) — handle with care re: ToS
