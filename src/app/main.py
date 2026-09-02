"""FastAPI application wiring (DI, webhook endpoints).

Story 1.1a ships only the skeleton: app factory + health routes. Telegram
webhook wiring arrives with Story 1.2; port adapters are wired here via DI in
later stories.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create the FastAPI application (entry for uvicorn / `python -m src.app`)."""
    app = FastAPI(title="zabota_mentor")

    @app.get("/")
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    # TODO (Story 1.2): Telegram webhook endpoint placeholder lands here.
    return app
