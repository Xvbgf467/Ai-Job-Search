FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# libgomp1 needed by faiss-cpu / scipy / torch (CPU)
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY app ./app
COPY scripts ./scripts

# On x86_64 use the small CPU-only torch wheel; on ARM (e.g. Oracle Ampere)
# let pip pick the aarch64 wheel from PyPI.
RUN pip install --upgrade pip && \
    if [ "$(uname -m)" = "x86_64" ]; then \
      pip install torch --index-url https://download.pytorch.org/whl/cpu; \
    fi && \
    pip install .

# Pre-download the embedding model so cold starts don't depend on the network
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Run as a non-root user (uid 1000) for portability across hosts
RUN useradd -m -u 1000 user && chown -R user:user /app
USER user

ENV HOME=/home/user \
    HF_HOME=/tmp/hf_cache \
    DATABASE_URL=sqlite:////tmp/techmatch.db

EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
