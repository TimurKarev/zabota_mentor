"""/start use case: salon deep-link entry point to onboarding (Story 1.2).

Pure-ish domain service over the ``ProfileRepository`` protocol — the Telegram
adapter delegates here (AD-10: transport, not state). Consent capture is
deliberately NOT here: it is Story 1.3, strictly after this story.
"""

from src.domain.profile.models import Salon, StartOutcome, StartResult
from src.domain.profile.repository import ProfileRepository

# Deterministic Russian templates (rendered_by: template spirit — no LLM here).
# The welcome names the salon so the master can confirm they landed in the
# right place; what comes next (onboarding) is mentioned without doing it.
WELCOME_TEMPLATE = (
    "Здравствуйте! Это «Забота» — помощник мастеров салона «{salon_name}».\n"
    "Сейчас мы немного познакомимся: я задам несколько вопросов, "
    "чтобы подсказки были полезными. Начнём, когда будете готовы."
)

FALLBACK_TEXT = (
    "Не удалось определить ваш салон. "
    "Пожалуйста, откройте бота по персональной ссылке вашего салона."
)


async def handle_start(
    repository: ProfileRepository, chat_id: int, start_payload: str | None
) -> StartResult:
    """Handle a /start command from ``chat_id`` with the deep-link payload.

    Unknown or missing payload creates no rows and returns the fallback;
    a known payload finds-or-creates the canonical master (AD-13), the
    ``chat_id <-> master_id`` mapping, and the salon-scoped work context
    (AD-7). Idempotent: repeated /start from the same chat reuses the same
    ``master_id`` — the repository guarantees that.
    """
    salon = await _resolve_salon(repository, start_payload)
    if salon is None:
        return StartResult(
            outcome=StartOutcome.SALON_NOT_IDENTIFIED,
            reply_text=FALLBACK_TEXT,
        )
    master_id = await repository.find_or_create_master_with_chat(chat_id)
    await repository.find_or_create_work_context(master_id, salon.salon_id)
    return StartResult(
        outcome=StartOutcome.SALON_IDENTIFIED,
        reply_text=WELCOME_TEMPLATE.format(salon_name=salon.name),
        master_id=master_id,
        salon_id=salon.salon_id,
    )


async def record_update_id_gate(
    repository: ProfileRepository, update_id: int
) -> bool:
    """Dedup gate for at-least-once delivery (AD-12): ``True`` if new update.

    The Telegram adapter checks this FIRST and skips silently on a repeat —
    a Telegram retry must be a no-op (AC #7).
    """
    return await repository.record_update_id(update_id)


async def _resolve_salon(
    repository: ProfileRepository, start_payload: str | None
) -> Salon | None:
    if not start_payload:
        return None
    return await repository.resolve_salon_by_start_code(start_payload)


__all__ = [
    "FALLBACK_TEXT",
    "WELCOME_TEMPLATE",
    "handle_start",
    "record_update_id_gate",
]
