"""Unit tests (always run, no DB) for the config editing boundary and resolution.

Story 1.1b: AC-1 (Pydantic-validated at the editing boundary) and the
active-version resolution rule, kept DB-free because both are pure.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from src.adapters.config_store import (
    ConfigInsertPayload,
    register_kind,
    resolve_active,
)
from src.adapters.config_store.models import KIND_PARAMS_MODELS, validate_params
from src.domain import ConfigVersion

AS_OF = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)


def _valid_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "author": "timur",
        "justification": "initial baseline",
        "valid_from": AS_OF,
        "params": {"alpha": 0.5},
        "kind": "params",
        "scope": "global",
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    "field",
    ["author", "justification"],
)
def test_editing_boundary_rejects_empty_strings(field: str) -> None:
    with pytest.raises(ValidationError):
        ConfigInsertPayload(**_valid_payload(**{field: "  "}))


def test_editing_boundary_rejects_naive_datetime() -> None:
    """AD-8: naive datetimes never reach the store."""
    naive = datetime(2026, 9, 3, 12, 0)
    with pytest.raises(ValidationError, match="timezone-aware"):
        ConfigInsertPayload(**_valid_payload(valid_from=naive))


def test_editing_boundary_rejects_non_object_params() -> None:
    with pytest.raises(ValidationError):
        ConfigInsertPayload(**_valid_payload(params=[1, 2, 3]))  # type: ignore[arg-type]


def test_editing_boundary_accepts_valid_payload() -> None:
    payload = ConfigInsertPayload(**_valid_payload())
    assert payload.author == "timur"
    assert payload.params == {"alpha": 0.5}


def test_validate_params_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="unknown config kind"):
        validate_params("prompt", {})


def test_validate_params_accepts_registered_structural_kind() -> None:
    assert validate_params("params", {"anything": True}) == {"anything": True}


def test_validate_params_uses_registered_typed_model() -> None:
    """The kind registry extension point: owning stories register typed schemas."""

    from pydantic import BaseModel

    class TypedParams(BaseModel):
        alpha: float

    register_kind("typed_test", TypedParams)
    try:
        assert validate_params("typed_test", {"alpha": 0.25}) == {"alpha": 0.25}
        with pytest.raises(ValidationError):
            validate_params("typed_test", {"alpha": "not a float"})
    finally:
        KIND_PARAMS_MODELS.pop("typed_test", None)


def _version(version: int, valid_from: datetime) -> ConfigVersion:
    return ConfigVersion(
        version=version,
        kind="params",
        scope="global",
        params={},
        author="timur",
        created_at=valid_from,
        valid_from=valid_from,
    )


def test_resolve_active_picks_greatest_valid_from_not_in_future() -> None:
    v1 = _version(1, AS_OF - timedelta(days=10))
    v2 = _version(2, AS_OF - timedelta(days=1))
    v3 = _version(3, AS_OF + timedelta(days=1))  # future: not yet active
    assert resolve_active([v1, v2, v3], AS_OF) == v2


def test_resolve_active_breaks_ties_on_version() -> None:
    """Activation inserts a new row that may share valid_from; version decides."""
    same_time = AS_OF - timedelta(hours=1)
    v4 = _version(4, same_time)
    v5 = _version(5, same_time)
    assert resolve_active([v4, v5], AS_OF) == v5


def test_resolve_active_returns_none_when_nothing_eligible() -> None:
    v1 = _version(1, AS_OF + timedelta(minutes=1))
    assert resolve_active([v1], AS_OF) is None
    assert resolve_active([], AS_OF) is None
