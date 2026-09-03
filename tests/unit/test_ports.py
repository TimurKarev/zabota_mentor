"""Smoke tests for the domain port Protocols (Story 1.1a, AC-2 / AC-7 / AC-8)."""

from datetime import datetime
from typing import Protocol

import pytest

from src.domain import Clock, ConfigStore, CrmPort, LlmPort, TelegramPort

PORTS = [CrmPort, LlmPort, TelegramPort, Clock, ConfigStore]


@pytest.mark.parametrize("port", PORTS, ids=lambda port: port.__name__)
def test_port_is_a_protocol_class(port: type) -> None:
    assert issubclass(port, Protocol)


@pytest.mark.parametrize(
    ("port", "governing_ad"),
    [
        (CrmPort, "AD-3"),
        (LlmPort, "AD-5"),
        (TelegramPort, "AD-10"),
        (Clock, "AD-8"),
        (ConfigStore, "AD-6"),
    ],
    ids=lambda value: value.__name__ if isinstance(value, type) else str(value),
)
def test_port_docstring_cites_its_governing_ad(port: type, governing_ad: str) -> None:
    """AC-2: each Protocol's docstring cites the architecture decision that governs it.

    The expected AD is stated per port, so a wrong or missing citation fails —
    unlike a bare "AD-" substring check, which any prose mentioning "AD-" passes.
    """
    assert port.__doc__ is not None
    assert governing_ad in port.__doc__, (
        f"{port.__name__} docstring does not cite its governing decision {governing_ad}"
    )


def test_clock_now_signature_returns_datetime() -> None:
    """The only fully specified signature at M0: an injectable time source.

    Timezone-awareness itself is an adapter contract — it gets a behavioral test
    once ``src/adapters/clock/`` exists (Story 1.1b+).
    """
    annotations = Clock.now.__annotations__
    assert annotations["return"] is datetime


def test_config_store_declares_the_full_1_1b_contract() -> None:
    """Story 1.1b evolved ConfigStore from a skeleton: insert/get/active/activate exist.

    Insert-only by shape — the port deliberately declares no update/delete
    (AD-6); the database-side guard is proven by the gated DB tests.
    """
    for method in ("insert", "get", "active", "activate"):
        assert hasattr(ConfigStore, method), f"ConfigStore is missing {method!r}"
    for forbidden in ("update", "delete"):
        assert not hasattr(ConfigStore, forbidden), (
            f"ConfigStore must not expose {forbidden!r} (AD-6 insert-only)"
        )
