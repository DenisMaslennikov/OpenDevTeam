"""FastAPI application factory for OpenDevTeam backend API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OpenDevTeam API",
    description="API для управления проектом OpenDevTeam",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Liveness/readiness probe endpoint."""
    return {"status": "ok"}
