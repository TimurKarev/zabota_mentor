# Multi-stage build for the zabota_mentor app/worker image (Story 1.1c).
# Stack pins per architecture M0: uv 0.12.9, Python 3.12, bookworm-slim base.

# ── Builder: resolve dependencies with uv into /app/.venv ─────────────────
# uv >= 0.10 no longer publishes `<version>-python3.12-bookworm-slim` composite
# tags (last was 0.9.30), so we take the pinned uv binary from the distroless
# image and run it on the slim Python base — the officially supported pattern.
FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependency layer first (manifest only) so source changes don't bust the
# dependency cache. The project is virtual for uv (`package = false`) —
# `--no-install-project` installs just the locked third-party deps.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Source + full sync. `migrations/` ships in the image so
# `python -m src.adapters.db.migrate` works in-container too.
COPY src ./src
COPY migrations ./migrations
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── Runtime: slim Python with the prebuilt venv ───────────────────────────
FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=. \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/src ./src
COPY --from=builder /app/migrations ./migrations

EXPOSE 8000

# App entry; the worker overrides this in docker-compose.yml (`src.worker`).
CMD ["python", "-m", "src.app"]
