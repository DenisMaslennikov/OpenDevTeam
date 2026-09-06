"""Entry point for OpenDevTeam backend API."""

import uvicorn
from uvicorn.config import Config


def run() -> None:
    """Run the backend API server."""
    config = Config(app="backend.app:app", host="0.0.0.0", port=8000, reload=True)
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    run()
