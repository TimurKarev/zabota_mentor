"""Unit tests for the /start domain service (Story 1.2, AC: #1..#5, #7).

Pure domain layer: the repository is a fake, no DB / no Telegram API. The
aiogram handler is exercised separately (tests/unit/test_telegram_webhook.py).
"""

from uuid import UUID

from src.domain.profile import (
    ProfileRepository,
    Salon,
    StartOutcome,
    handle_start,
    record_update_id_gate,
)

DEV_SALON = Salon(salon_id="dev-salon", name="Dev Salon", tz="Europe/Moscow")
DEV_SALON_BY_CODE = {"salon1": DEV_SALON}


class FakeRepository:
    """In-memory ProfileRepository: idempotent by construction, like the SQL."""

    def __init__(self, salons: dict[str, Salon]) -> None:
        # start_code -> salon
        self._salons = salons
        self._chat_to_master: dict[int, UUID] = {}
        self._work_contexts: set[tuple[UUID, str]] = set()
        self._update_ids: set[int] = set()

    async def resolve_salon_by_start_code(self, start_code: str) -> Salon | None:
        return self._salons.get(start_code)

    async def find_or_create_master_with_chat(self, chat_id: int) -> UUID:
        if chat_id not in self._chat_to_master:
            self._chat_to_master[chat_id] = UUID(
                f"00000000-0000-0000-0000-{chat_id:012d}"
            )
        return self._chat_to_master[chat_id]

    async def find_or_create_work_context(self, master_id: UUID, salon_id: str) -> None:
        self._work_contexts.add((master_id, salon_id))

    async def record_update_id(self, update_id: int) -> bool:
        if update_id in self._update_ids:
            return False
        self._update_ids.add(update_id)
        return True


async def test_start_with_known_payload_creates_master_mapping_context() -> None:
    """AC #1..#4: known payload -> master + chat mapping + work context."""
    repo = FakeRepository(DEV_SALON_BY_CODE)
    result = await handle_start(repo, chat_id=1001, start_payload="salon1")
    assert result.outcome is StartOutcome.SALON_IDENTIFIED
    assert result.master_id is not None
    assert repo._chat_to_master == {1001: result.master_id}
    assert repo._work_contexts == {(result.master_id, "dev-salon")}
    assert "Dev Salon" in result.reply_text


async def test_repeated_start_same_chat_reuses_master_id() -> None:
    """AC #2 / AD-13: repeated /start is idempotent by chat_id — one identity."""
    repo = FakeRepository(DEV_SALON_BY_CODE)
    first = await handle_start(repo, chat_id=1001, start_payload="salon1")
    second = await handle_start(repo, chat_id=1001, start_payload="salon1")
    assert second.master_id == first.master_id
    assert len(repo._chat_to_master) == 1
    assert repo._work_contexts == {(first.master_id, "dev-salon")}


async def test_unknown_payload_creates_nothing_and_falls_back() -> None:
    """Unknown payload -> no rows, fallback reply."""
    repo = FakeRepository(DEV_SALON_BY_CODE)
    result = await handle_start(repo, chat_id=1001, start_payload="nope")
    assert result.outcome is StartOutcome.SALON_NOT_IDENTIFIED
    assert result.master_id is None
    assert repo._chat_to_master == {}
    assert repo._work_contexts == set()


async def test_missing_payload_creates_nothing() -> None:
    """Plain /start (no payload) -> nothing created, fallback reply."""
    repo = FakeRepository(DEV_SALON_BY_CODE)
    result = await handle_start(repo, chat_id=1001, start_payload=None)
    assert result.outcome is StartOutcome.SALON_NOT_IDENTIFIED
    assert repo._chat_to_master == {}
    assert repo._work_contexts == set()


async def test_dedup_gate_first_and_second_sighting() -> None:
    """AC #7 / AD-12: update_id dedup — first sighting new, second seen."""
    repo = FakeRepository({})
    assert await record_update_id_gate(repo, update_id=42) is True
    assert await record_update_id_gate(repo, update_id=42) is False


async def test_welcome_text_is_the_module_template() -> None:
    """The welcome text comes from the deterministic template constant (2.3)."""
    from src.domain.profile.start import WELCOME_TEMPLATE

    repo = FakeRepository(DEV_SALON_BY_CODE)
    result = await handle_start(repo, chat_id=1001, start_payload="salon1")
    assert result.reply_text == WELCOME_TEMPLATE.format(salon_name="Dev Salon")


def test_fake_satisfies_the_published_protocol() -> None:
    """Structural check: the fake matches the ProfileRepository protocol."""
    assert isinstance(FakeRepository({}), ProfileRepository)
