"""Telegram port: the raw send abstraction over the Telegram Bot API.

Governing decision: AD-10 (Telegram is transport, not state).
Owning module: ``messaging`` — adapter home is ``src/adapters/telegram/``
(aiogram 3, Story 1.2).

Send-side quiet hours, pacing, and inline keyboards are enforced by the
dispatcher *before* this port is called; the port itself is a thin send
abstraction with no policy. Method signatures evolve with their implementing
stories — only what a story needs lands here.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class TelegramPort(Protocol):
    """Raw Telegram send abstraction — policy lives upstream in the dispatcher (AD-10)."""

    async def send_message(self, chat_id: int, text: str) -> None:
        """Send a plain-text message to ``chat_id``; raise on transport failure."""
        ...
