"""Clock port: the injectable time source.

Governing decisions: AD-2 (all externals behind ports), AD-8 (time and
timezones). Owning module: cross-cutting — adapter home is
``src/adapters/clock/``.

All time reads go through this port — never ``datetime.now()`` called directly.
This is what makes quiet-hours and DST logic testable: tests inject a frozen
or shifting Clock. Implementations return timezone-aware UTC datetimes.
"""

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Injectable time source; all time reads in the system go through it (AD-2, AD-8)."""

    def now(self) -> datetime:
        """Return the current time as a timezone-aware UTC datetime."""
        ...
