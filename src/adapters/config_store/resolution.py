"""Active-version resolution for the config store (AD-6, Story 1.1b).

Kept pure (no DB) so the resolution rule — greatest ``valid_from <= as_of``,
version as the tiebreak — is unit-testable without Postgres; the adapter calls
this helper, so prod and test share one implementation. Rows are human-edited
and few, so fetching a ``(kind, scope)`` group and resolving in Python is fine.
"""

from collections.abc import Iterable
from datetime import datetime

from src.domain import ConfigVersion


def resolve_active(
    versions: Iterable[ConfigVersion], as_of: datetime
) -> ConfigVersion | None:
    """The active version at ``as_of``: greatest ``valid_from <= as_of`` (version tiebreak)."""
    if as_of.tzinfo is None:
        raise ValueError("as_of must be timezone-aware (AD-8)")
    eligible = [version for version in versions if version.valid_from <= as_of]
    if not eligible:
        return None
    return max(eligible, key=lambda version: (version.valid_from, version.version))
