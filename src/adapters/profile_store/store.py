"""psycopg implementation of the profile slice of ``ProfileRepository``.

Sync psycopg style with an injected connection (``PostgresConfigStore``
conventions, Story 1.1b). The protocol methods are ``async`` because the
caller is the aiogram event loop; the bodies are fast single-statement sync
calls — fine at M0 pilot scale, revisit (``asyncio.to_thread``) if DB latency
ever blocks the loop measurably.
"""

from uuid import UUID

import psycopg

from src.domain.profile.models import Salon


class PostgresProfileStore:
    """Profile-schema repository: salons, canonical master identity, work context."""

    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    async def resolve_salon_by_start_code(self, start_code: str) -> Salon | None:
        """Resolve the salon a deep-link start code points at; ``None`` if unknown."""
        row = self._conn.execute(
            "SELECT salon_id, name, tz FROM profile.salon WHERE telegram_start_code = %s",
            (start_code,),
        ).fetchone()
        if row is None:
            return None
        return Salon(salon_id=row[0], name=row[1], tz=row[2])

    async def find_or_create_master_with_chat(self, chat_id: int) -> UUID:
        """Find or create the canonical master for ``chat_id`` (AD-13), idempotent.

        A transaction-scoped advisory lock keyed on ``chat_id`` serializes the
        find-or-create for the same chat (same pattern as the config store's
        version race), so a repeated or concurrent /start never produces a
        second ``master_id``.
        """
        with self._conn.transaction():
            self._conn.execute("SELECT pg_advisory_xact_lock(%s)", (chat_id,))
            row = self._conn.execute(
                "SELECT master_id FROM profile.master_chat_map WHERE chat_id = %s",
                (chat_id,),
            ).fetchone()
            if row is not None:
                return row[0]
            new_row = self._conn.execute(
                "INSERT INTO profile.master DEFAULT VALUES RETURNING master_id"
            ).fetchone()
            if new_row is None:
                raise RuntimeError(
                    "INSERT ... RETURNING produced no row — cannot happen for a "
                    "successful insert"
                )
            master_id = new_row[0]
            self._conn.execute(
                "INSERT INTO profile.master_chat_map (chat_id, master_id) VALUES (%s, %s)",
                (chat_id, master_id),
            )
            return master_id

    async def find_or_create_work_context(self, master_id: UUID, salon_id: str) -> None:
        """Ensure the salon-scoped work context exists (AD-7); idempotent."""
        with self._conn.transaction():
            self._conn.execute(
                "INSERT INTO profile.work_context (master_id, salon_id)"
                " VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (master_id, salon_id),
            )
