"""Entry point for `python -m src.app` — run the FastAPI app via uvicorn."""

import os

import uvicorn

from src.app.main import create_app


def main() -> None:
    # `or` fallback: a set-but-empty value (common in .env files / compose overrides)
    # falls back instead of crashing on int("") — Story 1.1b replaces this with
    # validated settings.
    host = os.getenv("APP_HOST") or "127.0.0.1"
    port = int(os.getenv("APP_PORT") or "8000")
    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    main()
