"""Editing-boundary validation for config inserts (Story 1.1b, AD-6).

Two layers, per the architecture:

1. Structural (here, now): non-empty author/justification, timezone-aware
   ``valid_from`` (AD-8), ``params`` as a JSON object, known ``kind``.
2. Typed per-kind params (extension point): the ``KIND_PARAMS_MODELS`` registry
   maps ``kind`` -> params model. Owning stories register their typed schemas
   (quiet hours, caps, corridors, ...) without touching the store; the full
   seed set is Story 7.5b. Nothing typed is registered yet — do not invent
   behavioral values here.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class ConfigInsertPayload(BaseModel):
    """Structural contract every config insert must satisfy before anything is written."""

    model_config = ConfigDict(frozen=True)

    author: str
    justification: str
    valid_from: datetime
    params: dict[str, Any]
    kind: str
    scope: str = "global"

    @field_validator("author", "justification", "kind", "scope")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must be a non-empty string")
        return value

    @field_validator("kind", "scope")
    @classmethod
    def _lowercase(cls, value: str) -> str:
        return value.lower()

    @field_validator("valid_from")
    @classmethod
    def _timezone_aware(cls, value: datetime) -> datetime:
        """AD-8: naive datetimes are rejected at the editing boundary."""
        if value.tzinfo is None:
            raise ValueError("valid_from must be timezone-aware (AD-8)")
        return value

    @field_validator("params")
    @classmethod
    def _json_object(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("params must be a JSON object")
        return value


# kind -> typed params model; None means structural-only validation (the
# current state of every kind). Later stories register via register_kind().
KIND_PARAMS_MODELS: dict[str, type[BaseModel] | None] = {"params": None}


def register_kind(kind: str, params_model: type[BaseModel] | None) -> None:
    """Register (or re-register) a config kind and its typed params model.

    Owning stories call this for their behavioral parameter schemas; the store
    itself never changes.
    """
    if not kind.strip():
        raise ValueError("kind must be a non-empty string")
    KIND_PARAMS_MODELS[kind.lower()] = params_model


def validate_params(kind: str, params: dict[str, Any]) -> dict[str, Any]:
    """Validate params against the registered model for ``kind`` (if any).

    Unknown kinds are rejected: the ``kind`` column discriminates params from
    future prompt artifacts (Story 6.1), and an unregistered kind has no
    validation contract to insert under.
    """
    params_model = KIND_PARAMS_MODELS.get(kind)
    if params_model is None:
        if kind not in KIND_PARAMS_MODELS:
            raise ValueError(
                f"unknown config kind {kind!r} — register it before inserting"
            )
        return params
    return dict(params_model.model_validate(params).model_dump())
