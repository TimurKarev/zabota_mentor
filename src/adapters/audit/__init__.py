"""Audit adapter — append-only audit event writer (AD-11, FR-14.2).

Lives adapter-side with no domain port in this story: the audit writes here
come from the config adapter (edge-side). When domain modules need to emit
audit events (Story 1.3 consent, Story 1.5 profile changes), that story decides
the coupling — nothing is pre-built here.

The full event catalogue (consent, egress, validator failures, erasure, sync
runs) lands with its owning stories; config inserts/activations are the first
real users of the log.
"""

from typing import Any

import psycopg
from psycopg.types.json import Jsonb
from pydantic import BaseModel, ConfigDict, field_validator


class AuditEvent(BaseModel):
    """One append-only audit record (``audit.event`` row shape)."""

    model_config = ConfigDict(frozen=True)

    event_type: str
    actor: str
    subject: dict[str, Any]
    inputs: dict[str, Any]
    justification: str
    salon_id: str | None = None

    @field_validator("justification")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("justification must be a non-empty string")
        return value


class AuditWriter:
    """Appends events to ``audit.event``; exposes no update or delete.

    ``justification`` is required — NOT NULL in the schema and in this
    signature: every significant decision is audited with a why (FR-14.2).
    ``salon_id`` stays ``None`` for global events (config changes); salon-scoped
    events start with Story 1.3 (AD-7).
    """

    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def append(
        self,
        *,
        event_type: str,
        actor: str,
        subject: dict[str, Any],
        inputs: dict[str, Any],
        justification: str,
        salon_id: str | None = None,
    ) -> None:
        """Append one audit event; ``occurred_at`` defaults to DB ``now()`` (UTC, AD-8)."""
        event = AuditEvent(
            event_type=event_type,
            actor=actor,
            subject=subject,
            inputs=inputs,
            justification=justification,
            salon_id=salon_id,
        )
        self._conn.execute(
            """
            INSERT INTO audit.event
                (event_type, actor, subject, inputs, justification, salon_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                event.event_type,
                event.actor,
                Jsonb(event.subject),
                Jsonb(event.inputs),
                event.justification,
                event.salon_id,
            ),
        )
