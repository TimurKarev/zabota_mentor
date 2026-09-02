"""Worker entry: scheduler, outbox dispatcher, sync jobs.

Story 1.1a ships only the idle skeleton — no DB, Redis, or Telegram connection
is required or opened. The placeholders below are implemented by later stories.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def run() -> None:
    """Run the worker loop: log startup and idle until cancelled.

    # TODO (Story 1.6+): outbox dispatcher — send-side quiet hours, pacing,
    #   dedup (Redis 8.x, never durable state — AD-4) before TelegramPort.
    # TODO (Story 1.7+): scheduled template sends (shift start, shift totals).
    # TODO (Epic 2): CRM sync jobs — webhook ingest and nightly reconcile.
    """
    logger.info("worker started; idling (no external connections in this story)")
    await asyncio.Event().wait()


def main() -> None:
    """Entry point for `python -m src.worker`."""
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("worker stopped")
