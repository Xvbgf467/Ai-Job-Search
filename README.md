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

## CLI

Match a resume from the terminal:

```bash
python scripts/match.py path/to/resume.pdf --name "Jane Doe" --top 10
python scripts/match.py cv.docx --role ai_llm_engineer --fetch
```

## Deployment

Containerized via Docker (image ~2 GB due to PyTorch + embeddings). The app
listens on `$PORT` (default **7860**) and seeds jobs on startup.

Quick run:

```bash
docker compose up -d --build      # uses docker-compose.yml + .env
# or manually:
docker build -t techmatch .
docker run -p 7860:7860 --env-file .env techmatch
```

Put `LLM_*` in a `.env` file (never bake the key into the image). The embedding
model is pre-downloaded during build, so cold starts need no network.

### Oracle Cloud Always Free (recommended free host)

The Ampere A1 VM (up to 4 OCPU / 24 GB RAM) runs the full PyTorch app for free.

1. Create an Always Free account and an **VM.Standard.A1.Flex** instance
   (Ubuntu 22.04). Note its public IP.
2. In the OCI console open the VCN **Security List** ingress: `0.0.0.0/0` TCP `7860`.
3. SSH in and run the one-shot setup script:

```bash
curl -fsSL https://raw.githubusercontent.com/Xvbgf467/Ai-Job-Search/main/deploy/oracle/setup.sh | bash
# follow the prompts (install Docker, set LLM_API_KEY in .env), then re-run it
```

The app is then live at `http://<public-ip>:7860`.

### Google Colab (free, temporary demo)

No account beyond Google, no credit card. Open the notebook and **Run All**:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Xvbgf467/Ai-Job-Search/blob/main/notebooks/colab_demo.ipynb)

It reuses Colab's bundled PyTorch (fast install), exposes the app via a free
Cloudflare quick-tunnel, and prints a public URL. The URL is per-session — it
dies when the Colab session disconnects/idles (re-run to restart).

Other hosts (need ~2 GB RAM for PyTorch): **Hugging Face Spaces** (Docker, now
requires Pro), **Railway / Fly.io / Koyeb** (~$5/mo or free tier).

## Status

Done: resume parsing, skill/role taxonomy, sourcing (Remotive + HN),
keyword + embedding scorer, LLM re-rank (Z.AI GLM), dashboard UI,
background fetcher, CLI, Docker.

Todo: dashboard filters, application tracking, LinkedIn/Indeed scrapers (mind ToS).
