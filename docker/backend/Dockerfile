FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY packages/ ./packages/

RUN uv sync --frozen --no-dev --package opendevteam-backend

COPY . .

ENV PYTHONPATH=/app/packages/backend/src
CMD ["uv", "run", "--no-sync", "uvicorn", "backend.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
