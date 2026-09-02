"""Telegram port: the raw send abstraction over the Telegram Bot API.

Governing decision: AD-10 (Telegram is transport, not state).
Owning module: ``messaging`` — adapter home is ``src/adapters/telegram/``
(aiogram 3 wiring lands with Story 1.2).

Send-side quiet hours, pacing, and inline keyboards are enforced by the
dispatcher *before* this port is called; the port itself is a thin send
abstraction with no policy.

# TODO (Story 1.2): send and keyboard method signatures evolve with their
# implementing stories — deliberately not invented here.
"""

from typing import Protocol


class TelegramPort(Protocol):
    """Raw Telegram send abstraction — policy lives upstream in the dispatcher (AD-10)."""
