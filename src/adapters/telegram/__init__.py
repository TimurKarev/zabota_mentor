"""Telegram adapter — implements TelegramPort (raw send) on top of aiogram 3.

Owns the aiogram wiring (Bot / Dispatcher / Router / middlewares) for the
``messaging`` module's transport side (Story 1.2). Business decisions stay in
``src.domain.profile``; this package is transport only (AD-10).
"""

from src.adapters.telegram.port import AiogramTelegramPort
from src.adapters.telegram.start_router import (
    BotDependencies,
    RepositoryFactory,
    build_bot,
    build_dispatcher,
    create_start_router,
)

__all__ = [
    "AiogramTelegramPort",
    "BotDependencies",
    "RepositoryFactory",
    "build_bot",
    "build_dispatcher",
    "create_start_router",
]
