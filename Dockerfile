FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install uv
RUN pip install --no-cache-dir uv

# ----- Dependencies -----
# Copy project metadata + README
COPY pyproject.toml uv.lock .python-version README.md ./

# Copy source code so `src/` exists when uv builds the project
COPY src ./src

# Install deps from lockfile into .venv
RUN uv sync --locked --no-dev --no-cache

# Use uv's venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Make src importable
ENV PYTHONPATH=/app/src

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/docs || exit 1

CMD ["bash", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -w ${WORKERS:-2} -b 0.0.0.0:8000 resume_chatbot_api.app:app"]
