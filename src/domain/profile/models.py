"""Domain models for the profile module's /start slice (Story 1.2).

Entity models for psych profiling / consent land with Stories 1.3–1.5; these
are the minimal identity + result models the /start command needs (AD-13).
"""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Salon(BaseModel):
    """A salon known via its deep-link start code (AD-7 scoping anchor)."""

    model_config = ConfigDict(frozen=True)

    salon_id: str
    name: str
    tz: str


class StartOutcome(Enum):
    """What handle_start decided — drives the adapter's reply choice."""

    SALON_IDENTIFIED = "salon_identified"
    SALON_NOT_IDENTIFIED = "salon_not_identified"


class StartResult(BaseModel):
    """Outcome of a /start command: the decision plus the reply text to send.

    The domain composes the reply text from its template constants so the
    transport layer stays policy-free (AD-10) — the adapter only delivers it.
    """

    model_config = ConfigDict(frozen=True)

    outcome: StartOutcome
    reply_text: str
    master_id: UUID | None = None
    salon_id: str | None = None
