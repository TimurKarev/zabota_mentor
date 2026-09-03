"""Config store adapter — versioned config storage behind ConfigStore (AD-6).

Implementation over psycopg (Story 1.1b): :class:`PostgresConfigStore` plus the
editing-boundary validation models and the pure active-version resolution rule.
A library until later stories consume it — ``src.app`` / ``src.worker`` keep
starting DB-free (first consumer is Story 1.6).
"""

from src.adapters.config_store.models import (
    KIND_PARAMS_MODELS,
    ConfigInsertPayload,
    register_kind,
    validate_params,
)
from src.adapters.config_store.resolution import resolve_active
from src.adapters.config_store.store import PostgresConfigStore

__all__ = [
    "KIND_PARAMS_MODELS",
    "ConfigInsertPayload",
    "PostgresConfigStore",
    "register_kind",
    "resolve_active",
    "validate_params",
]
