"""Durable ``update_id`` dedup over psycopg (AD-12, Story 1.2)."""

import psycopg


class PostgresUpdateDedup:
    """Insert-only dedup gate for at-least-once Telegram delivery."""

    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    async def record_update_id(self, update_id: int) -> bool:
        """Record an update; ``True`` if this is the first sighting.

        ``False`` means the update was already processed — the caller must
        skip it silently so a Telegram retry is a no-op (AC #7).
        """
        with self._conn.transaction():
            cursor = self._conn.execute(
                "INSERT INTO messaging.telegram_update_dedup (update_id)"
                " VALUES (%s) ON CONFLICT (update_id) DO NOTHING",
                (update_id,),
            )
            return cursor.rowcount == 1
