"""Postgres implementation of the messaging-dedup slice (Story 1.2, AD-12).

Owns the ``messaging`` schema (AD-11) — the durable ``update_id`` dedup table
created by ``migrations/0002_profile_master_tables.sql``. The table is
insert-only: the row IS the marker, and a Telegram retry hits
``ON CONFLICT DO NOTHING`` so reprocessing is a no-op (AC #7).

Redis stays unwired (AD-4) — a Redis dedup layer is a later optimization
(Story 1.6), never the durable source of truth.
"""

from src.adapters.messaging_store.dedup import PostgresUpdateDedup

__all__ = ["PostgresUpdateDedup"]
