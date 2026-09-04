"""Telegram runtime composition root (Story 1.2).

Builds the production ``BotDependencies``: one psycopg connection per update,
wrapped in a composite repository that satisfies the domain's
``ProfileRepository`` protocol by delegating to the profile store (profile
schema) and the messaging dedup store (messaging schema). Kept in ``src.app``
because composing adapters is application wiring, not adapter behavior
(AD-11: each adapter package stays inside its own schema).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

import psycopg
from aiogram import Bot

from src.adapters.messaging_store import PostgresUpdateDedup
from src.adapters.profile_store import PostgresProfileStore
from src.adapters.telegram import AiogramTelegramPort, BotDependencies
from src.domain.profile import ProfileRepository
from src.domain.profile.models import Salon


class PostgresStartRepository:
    """ProfileRepository over one psycopg connection, per Telegram update.

    Composite by design: the three profile-schema methods live in
    ``src/adapters/profile_store``, the durable dedup method in
    ``src/adapters/messaging_store`` — both share the connection, and
    ``open_repository`` below wraps the whole update in ONE transaction
    (the per-method ``conn.transaction()`` blocks nest as savepoints), so the
    dedup marker and all profile rows commit or roll back together.
    """

    def __init__(self, conn: psycopg.Connection) -> None:
        self._profile = PostgresProfileStore(conn)
        self._dedup = PostgresUpdateDedup(conn)

    async def resolve_salon_by_start_code(self, start_code: str) -> Salon | None:
        return await self._profile.resolve_salon_by_start_code(start_code)

    async def find_or_create_master_with_chat(self, chat_id: int) -> UUID:
        return await self._profile.find_or_create_master_with_chat(chat_id)

    async def find_or_create_work_context(self, master_id: UUID, salon_id: str) -> None:
        await self._profile.find_or_create_work_context(master_id, salon_id)

    async def record_update_id(self, update_id: int) -> bool:
        return await self._dedup.record_update_id(update_id)


def telegram_bot_dependencies(database_url: str, bot: Bot) -> BotDependencies:
    """Production wiring: a fresh connection + repository per Telegram update."""

    @asynccontextmanager
    async def open_repository() -> AsyncIterator[ProfileRepository]:
        # One transaction per update (AD-12): the dedup marker and all rows
        # written by the handler commit together on clean exit and roll back
        # together on failure — a failed update leaves no dedup row behind,
        # so Telegram's retry reprocesses it instead of dropping it.
        # connect_timeout bounds the blocking handshake on the event loop.
        with psycopg.connect(database_url, connect_timeout=3) as conn, conn.transaction():
            yield PostgresStartRepository(conn)

    return BotDependencies(open_repository=open_repository, telegram=AiogramTelegramPort(bot))
