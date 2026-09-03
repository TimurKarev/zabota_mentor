"""Config store port: insert-only versioned configuration and prompt artifacts.

Governing decision: AD-6 (versioned configuration).
Owning module: ``config`` — adapter home is ``src/adapters/config_store/``.

Configuration and prompt artifacts are insert-only; readers fetch by version at
decision time, so compute and send never span versions and behavior is
reproducible. Values are Pydantic-validated at the editing boundary
(schema-layer convention). Rollback is itself an insert — activating a prior
version writes a NEW row with a fresh ``valid_from`` (no UPDATE-based rollback),
which makes the < 5 min rollback requirement (FR-14.1) mechanical. Every insert
and activation is an audit event (FR-14.2).
"""

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict


class ConfigVersion(BaseModel):
    """One immutable, version-addressed config row (AD-6 shape).

    ``kind`` discriminates ``params`` from future prompt artifacts (Story 6.1);
    ``scope`` defaults to ``'global'`` — per-salon owner settings arrive with
    Story 3.0.
    """

    model_config = ConfigDict(frozen=True)

    version: int
    kind: str
    scope: str
    params: dict[str, Any]
    author: str
    created_at: datetime
    valid_from: datetime


class ConfigStore(Protocol):
    """Insert-only, version-addressed configuration and prompt artifact store (AD-6).

    The store exposes no update or delete: rows are immutable after insert, and
    the database enforces it (trigger guard, see ``migrations/``). The active
    version at decision time is the row with the greatest ``valid_from <= now``
    for its ``(kind, scope)``; callers resolve per decision — never cached
    across a decision.
    """

    def insert(
        self,
        params: Mapping[str, Any],
        *,
        author: str,
        justification: str,
        valid_from: datetime,
        kind: str = "params",
        scope: str = "global",
    ) -> ConfigVersion:
        """Validate and insert a new versioned row; writes an audit event.

        Params are Pydantic-validated at this editing boundary (structural rules
        plus the registered per-kind model, if any) before anything is written.
        """
        ...

    def get(
        self, version: int, *, kind: str = "params", scope: str = "global"
    ) -> ConfigVersion | None:
        """Fetch one row by its version address; ``None`` if it does not exist."""
        ...

    def active(
        self, as_of: datetime, *, kind: str = "params", scope: str = "global"
    ) -> ConfigVersion | None:
        """Resolve the active version at ``as_of`` (greatest ``valid_from <= as_of``)."""
        ...

    def activate(
        self,
        prior_version: int,
        *,
        author: str,
        justification: str,
        valid_from: datetime,
        kind: str = "params",
        scope: str = "global",
    ) -> ConfigVersion:
        """Activate a prior version by inserting a NEW row with its params (AD-6).

        Rollback without UPDATE: the new row carries a fresh ``valid_from``, so
        ``active()`` moves to it at decision time. Audited like any insert.
        """
        ...
