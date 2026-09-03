"""Postgres implementation of the ConfigStore port (AD-6, Story 1.1b).

Rows live in the ``config`` schema and are immutable after insert: this class
exposes no update/delete, and the database rejects them regardless of role
(trigger guard in ``migrations/0001_config_and_audit_schemas.sql``). Every
insert and activation writes an audit event with justification + inputs via
``src/adapters/audit`` (FR-14.2).

Sync psycopg signatures — the adapter is the only implementation so far; one
style, kept consistent.
"""

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from src.adapters.audit import AuditWriter
from src.adapters.config_store.models import ConfigInsertPayload, validate_params
from src.adapters.config_store.resolution import resolve_active
from src.domain import ConfigVersion

_COLUMNS = (
    "version, kind, scope, params, author, created_at, valid_from"
)


class PostgresConfigStore:
    """Insert-only, version-addressed config store over a psycopg connection.

    The optional ``audit`` writer must share the same connection as ``conn`` so
    that config inserts and their audit events commit atomically. Passing an
    ``AuditWriter`` on a different connection breaks that invariant.
    """

    def __init__(self, conn: psycopg.Connection, audit: AuditWriter | None = None) -> None:
        self._conn = conn
        self._audit = audit if audit is not None else AuditWriter(conn)

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
        """Validate at the editing boundary, insert a new version, audit it."""
        payload = ConfigInsertPayload(
            author=author,
            justification=justification,
            valid_from=valid_from,
            params=dict(params),
            kind=kind,
            scope=scope,
        )
        validated = validate_params(payload.kind, payload.params)
        return self._insert_row(
            validated,
            author=payload.author,
            justification=payload.justification,
            valid_from=payload.valid_from,
            kind=payload.kind,
            scope=payload.scope,
            event_type="config.insert",
        )

    def get(
        self, version: int, *, kind: str = "params", scope: str = "global"
    ) -> ConfigVersion | None:
        """Fetch one row by its version address; ``None`` if it does not exist."""
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM config.config_version"
            " WHERE kind = %s AND scope = %s AND version = %s",
            (kind, scope, version),
        ).fetchone()
        return _to_config_version(row) if row is not None else None

    def active(
        self, as_of: datetime, *, kind: str = "params", scope: str = "global"
    ) -> ConfigVersion | None:
        """Resolve the active version at ``as_of`` (readers fetch per decision, AD-6)."""
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM config.config_version"
            " WHERE kind = %s AND scope = %s ORDER BY valid_from, version",
            (kind, scope),
        ).fetchall()
        return resolve_active((_to_config_version(row) for row in rows), as_of)

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

        Rollback without UPDATE: the fresh ``valid_from`` moves ``active()`` to
        the new row, so config rollback is an insert (FR-14.1).
        """
        # Validate editing-boundary inputs before the DB lookup so invalid
        # kind/scope/valid_from surface as validation errors, not as a
        # misleading "cannot activate nonexistent config version".
        pre = ConfigInsertPayload(
            author=author,
            justification=justification,
            valid_from=valid_from,
            params={},
            kind=kind,
            scope=scope,
        )
        prior = self.get(prior_version, kind=pre.kind, scope=pre.scope)
        if prior is None:
            raise ValueError(
                f"cannot activate nonexistent config version "
                f"{prior_version} (kind={pre.kind!r}, scope={pre.scope!r})"
            )
        # Activation goes through the same editing boundary as any insert.
        validated = validate_params(prior.kind, prior.params)
        return self._insert_row(
            validated,
            author=pre.author,
            justification=pre.justification,
            valid_from=pre.valid_from,
            kind=prior.kind,
            scope=prior.scope,
            event_type="config.activate",
            subject_extra={"prior_version": prior_version},
        )

    def _insert_row(
        self,
        params: dict[str, Any],
        *,
        author: str,
        justification: str,
        valid_from: datetime,
        kind: str,
        scope: str,
        event_type: str,
        subject_extra: dict[str, Any] | None = None,
    ) -> ConfigVersion:
        """Insert the next version for ``(kind, scope)`` and append its audit event.

        A transaction-scoped advisory lock keyed on ``(kind, scope)`` serializes
        concurrent inserts for the same group, preventing MAX(version)+1 races.
        Config edits are rare and human-driven; the lock allows parallelism
        across different kinds/scopes.
        """
        with self._conn.transaction():
            self._conn.execute(
                "SELECT pg_advisory_xact_lock(hashtext(%s))", (
                    f"{kind}:{scope}",)
            )
            max_row = self._conn.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM config.config_version"
                " WHERE kind = %s AND scope = %s",
                (kind, scope),
            ).fetchone()
            next_version = max_row[0] if max_row is not None else 1
            row = self._conn.execute(
                f"INSERT INTO config.config_version ({_COLUMNS})"
                " VALUES (%s, %s, %s, %s, %s, now(), %s)"
                f" RETURNING {_COLUMNS}",
                (next_version, kind, scope, Jsonb(params), author, valid_from),
            ).fetchone()
            if row is None:
                raise RuntimeError(
                    "INSERT ... RETURNING produced no row — cannot happen for a "
                    "successful insert"
                )
            version = _to_config_version(row)
            subject = {"kind": kind, "scope": scope,
                       "version": version.version}
            if subject_extra:
                subject.update(subject_extra)
            self._audit.append(
                event_type=event_type,
                actor=author,
                subject=subject,
                inputs={"params": params},
                justification=justification,
            )
        return version


def _to_config_version(row: tuple[Any, ...]) -> ConfigVersion:
    """Map a SELECT/RETURNING row (column order of ``_COLUMNS``) to a ConfigVersion."""
    return ConfigVersion(
        version=row[0],
        kind=row[1],
        scope=row[2],
        params=dict(row[3]),
        author=row[4],
        created_at=row[5],
        valid_from=row[6],
    )
