"""Repository protocol for the profile module (Story 1.2, AD-13, AD-12).

Domain purity: no psycopg / aiogram imports here (import-linter, AD-2). The
psycopg implementation lives in ``src/adapters/profile_store`` (profile
schema) and ``src/adapters/messaging_store`` (messaging schema, dedup only).
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

from src.domain.profile.models import Salon


@runtime_checkable
class ProfileRepository(Protocol):
    """Persistence surface the /start use case needs.

    Implementations must be idempotent: a repeated /start from the same chat
    reuses the same ``master_id`` (one canonical identity, AD-13), and a
    repeated ``update_id`` is reported as already seen (AD-12).
    """

    async def resolve_salon_by_start_code(self, start_code: str) -> Salon | None:
        """Resolve the salon a deep-link payload points at; ``None`` if unknown."""
        ...

    async def find_or_create_master_with_chat(self, chat_id: int) -> UUID:
        """Find or create the canonical master for ``chat_id`` (idempotent).

        Also ensures the ``chat_id <-> master_id`` mapping exists (AD-13).
        """
        ...

    async def find_or_create_work_context(self, master_id: UUID, salon_id: str) -> None:
        """Find or create the salon-scoped work context (AD-7), idempotent."""
        ...

    async def record_update_id(self, update_id: int) -> bool:
        """Record a Telegram ``update_id``; ``True`` if first sighting (AD-12)."""
        ...
