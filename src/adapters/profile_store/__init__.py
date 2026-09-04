"""Postgres implementation of the profile repository (Story 1.2, AD-13, AD-7).

Owns the ``profile`` schema (AD-11) — the salon / master / chat-map /
work-context tables created by ``migrations/0002_profile_master_tables.sql``.
The ``messaging`` dedup method of the published protocol is implemented by
``src/adapters/messaging_store`` and composed at the application root.
"""

from src.adapters.profile_store.store import PostgresProfileStore

__all__ = ["PostgresProfileStore"]
