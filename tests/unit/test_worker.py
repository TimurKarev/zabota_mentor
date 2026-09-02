"""Tests for the worker entry skeleton (Story 1.1a, AC-6)."""

import asyncio
import logging

import pytest

from src.worker import main as worker_main


def test_worker_run_is_a_coroutine_function() -> None:
    """`run()` is awaitable and takes no required external dependencies."""
    assert asyncio.iscoroutinefunction(worker_main.run)


async def test_worker_logs_startup_and_idles_until_cancelled(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        task = asyncio.create_task(worker_main.run())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert any("worker started" in record.message for record in caplog.records)
