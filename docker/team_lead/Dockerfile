FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY packages/ ./packages/

RUN uv sync --frozen --no-dev --package opendevteam-team-lead

COPY . .

ENV PYTHONPATH=/app/packages/agents/team_lead/src
CMD ["uv", "run", "--no-sync", "python", "-m", "team_lead.main"]
