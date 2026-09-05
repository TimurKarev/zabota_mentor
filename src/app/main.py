"""FastAPI application wiring (DI, webhook endpoints).

Story 1.1a shipped the skeleton; Story 1.2 adds the Telegram runtime: the
bot + dispatcher are constructed in the FastAPI lifespan when ``BOT_TOKEN``
(and ``DATABASE_URL``) are set — webhook mode in prod, polling in dev — and
the webhook endpoint feeds updates to the dispatcher. With no token the app
degrades to ``/health`` only (regression guard: app starts with no external
deps and CI depends on it).
"""

import asyncio
import hmac
import logging
import os
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager, suppress

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException

from src.adapters.telegram import build_bot, build_dispatcher
from src.app.telegram import telegram_bot_dependencies

logger = logging.getLogger(__name__)

TELEGRAM_WEBHOOK_PATH = "/telegram/webhook"


def _log_polling_failure(task: asyncio.Task[None]) -> None:
    """Surface polling-task death — otherwise /health stays green with a dead bot."""
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error("Telegram polling stopped with an error", exc_info=exc)


def _build_lifespan(
    bot_override: Bot | None, dispatcher_override: Dispatcher | None
) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    """Build the lifespan closure: bot lifecycle per env, or test overrides."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Test injection path: the caller supplied a prebuilt bot/dispatcher
        # (fake deps) — mount them without any Telegram API traffic.
        if bot_override is not None and dispatcher_override is not None:
            app.state.bot = bot_override
            app.state.dispatcher = dispatcher_override
            try:
                yield
            finally:
                with suppress(Exception):
                    await bot_override.session.close()
            return

        token = os.getenv("BOT_TOKEN")
        database_url = os.getenv("DATABASE_URL")
        if not token or not database_url:
            logger.warning(
                "BOT_TOKEN%s set — serving /health only (no Telegram bot).",
                "/DATABASE_URL not" if token else " not",
            )
            yield
            return

        proxy = os.getenv("TG_PROXY_URL") or None
        if proxy:
            logger.info("Telegram traffic routed via proxy: %s", proxy)
        bot = build_bot(token, proxy=proxy)
        deps = telegram_bot_dependencies(database_url, bot)
        dispatcher = build_dispatcher(deps)
        app.state.bot = bot
        app.state.dispatcher = dispatcher

        mode = (os.getenv("BOT_MODE") or "polling").strip().lower()
        poll_task: asyncio.Task[None] | None = None
        try:
            if mode not in {"webhook", "polling"}:
                # Fail fast: a typo would otherwise silently run polling.
                raise RuntimeError(
                    f"Invalid BOT_MODE {os.getenv('BOT_MODE')!r} — "
                    "must be 'webhook' or 'polling'"
                )
            if mode == "webhook":
                base_url = os.getenv("WEBHOOK_URL") or ""
                secret = os.getenv("TELEGRAM_SECRET_TOKEN") or None
                if not base_url or not secret:
                    logger.error(
                        "BOT_MODE=webhook needs WEBHOOK_URL and TELEGRAM_SECRET_TOKEN "
                        "— set_webhook skipped; bot will receive nothing until it is set."
                    )
                else:
                    await bot.set_webhook(
                        url=f"{base_url.rstrip('/')}{TELEGRAM_WEBHOOK_PATH}",
                        secret_token=secret,
                    )
            else:
                # Dev mode: no public URL needed — long polling in the
                # background. handle_signals=False: uvicorn owns SIGTERM.
                poll_task = asyncio.create_task(
                    dispatcher.start_polling(bot, handle_signals=False)
                )
                poll_task.add_done_callback(_log_polling_failure)
            yield
        finally:
            if poll_task is not None:
                poll_task.cancel()
                # The done-callback already logged a real failure; a stored
                # exception must not also break shutdown.
                with suppress(asyncio.CancelledError, Exception):
                    await poll_task
            await bot.session.close()

    return lifespan


def create_app(
    *,
    bot: Bot | None = None,
    dispatcher: Dispatcher | None = None,
) -> FastAPI:
    """Create the FastAPI application (entry for uvicorn / `python -m src.app`).

    ``bot`` / ``dispatcher`` are injection points for tests (fake deps, no
    real Telegram API) and must be passed together. Production wiring is
    env-driven inside the lifespan: ``BOT_TOKEN`` + ``DATABASE_URL`` set ->
    bot runs; otherwise a warning and ``/health`` only.
    """
    if (bot is None) != (dispatcher is None):
        raise ValueError("bot and dispatcher must be injected together")
    app = FastAPI(title="zabota_mentor", lifespan=_build_lifespan(bot, dispatcher))

    @app.get("/")
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(TELEGRAM_WEBHOOK_PATH)
    async def telegram_webhook(
        update: Update,
        x_telegram_bot_api_secret_token: str | None = Header(default=None),
    ) -> dict[str, str]:
        """Receive one Telegram update and hand it to the dispatcher (AC #6).

        Constant-time secret check (Telegram sends the header only when
        ``set_webhook`` was called with a ``secret_token``); a retry after a
        non-200/timeout reprocesses cleanly thanks to the per-update
        transaction + update_id dedup (AD-12). Bytes on both sides:
        compare_digest rejects non-ASCII str with a TypeError.
        """
        expected = os.getenv("TELEGRAM_SECRET_TOKEN")
        if not expected:
            raise HTTPException(
                status_code=503,
                detail="TELEGRAM_SECRET_TOKEN is not configured — webhook disabled.",
            )
        provided = x_telegram_bot_api_secret_token
        if provided is None:
            raise HTTPException(status_code=401, detail="missing secret token header")
        if not hmac.compare_digest(provided.encode(), expected.encode()):
            raise HTTPException(status_code=403, detail="bad secret token")
        dispatcher: Dispatcher | None = getattr(app.state, "dispatcher", None)
        active_bot: Bot | None = getattr(app.state, "bot", None)
        if dispatcher is None or active_bot is None:
            raise HTTPException(
                status_code=503, detail="Telegram bot is not running (no BOT_TOKEN?)."
            )
        await dispatcher.feed_webhook_update(active_bot, update)
        return {"status": "ok"}

    return app
