"""Config store port: insert-only versioned configuration and prompt artifacts.

Governing decision: AD-6 (versioned configuration).
Owning module: ``config`` — adapter home is ``src/adapters/config_store/``
(implementation lands with Story 1.1b).

Configuration and prompt artifacts are insert-only; readers fetch by version at
decision time, so behavior is reproducible and auditable. Values are
Pydantic-validated at the editing boundary (schema-layer convention).

# TODO (Story 1.1b): read/write method signatures and the audit trail evolve
# with the implementing story — deliberately not invented here.
"""

from typing import Protocol


class ConfigStore(Protocol):
    """Insert-only, version-addressed configuration and prompt artifact store (AD-6)."""
