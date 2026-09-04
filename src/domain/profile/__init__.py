"""Profile module — master/client profiles, consent, dynamic profiling state.

Published interface for cross-module access (AD-11). The /start slice
(Story 1.2) starts this surface; entity models for psych profiling and
consent land with Stories 1.3–1.5 / Epic 2.
"""

from src.domain.profile.models import Salon, StartOutcome, StartResult
from src.domain.profile.repository import ProfileRepository
from src.domain.profile.start import (
    FALLBACK_TEXT,
    WELCOME_TEMPLATE,
    handle_start,
    record_update_id_gate,
)

__all__ = [
    "FALLBACK_TEXT",
    "ProfileRepository",
    "Salon",
    "StartOutcome",
    "StartResult",
    "WELCOME_TEMPLATE",
    "handle_start",
    "record_update_id_gate",
]
