"""DB-backed contract tests for the profile store + dedup (Story 1.2, AC #2..#4, #7).

Gated on ``TEST_DATABASE_URL`` (PostgreSQL 17), same pattern as
``test_config_store_db.py``: without the env var they skip visibly; the unit
layer stays fully green without Docker. Isolation is per-test unique values —
never TRUNCATE.
"""

import os
import uuid
from collections.abc import Iterator
from random import randrange

import psycopg
import pytest

from src.adapters.db.migrate import apply_pending
from src.adapters.messaging_store import PostgresUpdateDedup
from src.adapters.profile_store import PostgresProfileStore

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is not set — DB-backed tests need a PostgreSQL 17 "
    "(see README: docker run --rm -e POSTGRES_PASSWORD=... -p 5432:5432 postgres:17)",
)


@pytest.fixture
def conn() -> Iterator[psycopg.Connection]:
    """Connection with migrations applied; the runner is idempotent per test."""
    with psycopg.connect(TEST_DATABASE_URL) as connection:
        apply_pending(connection)
        yield connection


@pytest.fixture
def store(conn: psycopg.Connection) -> PostgresProfileStore:
    return PostgresProfileStore(conn)


def _unique_chat_id() -> int:
    """Isolation without TRUNCATE: each test uses its own chat_id."""
    # Positive int63 well below bigint overflow even with the sign trick.
    return randrange(10**12, 10**15)


def _unique_salon(conn: psycopg.Connection) -> str:
    """Insert a throwaway salon (unique start code) and return its salon_id."""
    salon_id = f"test-salon-{uuid.uuid4().hex[:12]}"
    conn.execute(
        "INSERT INTO profile.salon (salon_id, telegram_start_code, name)"
        " VALUES (%s, %s, %s)",
        (salon_id, f"code-{uuid.uuid4().hex[:12]}", "Contract Test Salon"),
    )
    return salon_id


async def test_find_or_create_master_is_idempotent_by_chat_id(
    store: PostgresProfileStore, conn: psycopg.Connection
) -> None:
    """AC #2/#3: repeated find-or-create yields ONE master_id and one mapping row."""
    chat_id = _unique_chat_id()
    first = await store.find_or_create_master_with_chat(chat_id)
    second = await store.find_or_create_master_with_chat(chat_id)
    assert first == second
    rows = conn.execute(
        "SELECT master_id FROM profile.master_chat_map WHERE chat_id = %s",
        (chat_id,),
    ).fetchall()
    assert len(rows) == 1
    masters = conn.execute(
        "SELECT count(*) FROM profile.master WHERE master_id = %s", (first,)
    ).fetchone()
    assert masters is not None and masters[0] == 1


async def test_work_context_find_or_create_is_idempotent(
    store: PostgresProfileStore, conn: psycopg.Connection
) -> None:
    """AC #4: repeated work-context creation leaves exactly one row (AD-7)."""
    chat_id = _unique_chat_id()
    salon_id = _unique_salon(conn)
    master_id = await store.find_or_create_master_with_chat(chat_id)
    await store.find_or_create_work_context(master_id, salon_id)
    await store.find_or_create_work_context(master_id, salon_id)
    rows = conn.execute(
        "SELECT count(*) FROM profile.work_context WHERE master_id = %s AND salon_id = %s",
        (master_id, salon_id),
    ).fetchone()
    assert rows is not None and rows[0] == 1


async def test_work_context_supports_two_salons_per_master(
    store: PostgresProfileStore, conn: psycopg.Connection
) -> None:
    """AD-7 foundation: one master, N salon-scoped work contexts."""
    chat_id = _unique_chat_id()
    salon_a = _unique_salon(conn)
    salon_b = _unique_salon(conn)
    master_id = await store.find_or_create_master_with_chat(chat_id)
    await store.find_or_create_work_context(master_id, salon_a)
    await store.find_or_create_work_context(master_id, salon_b)
    rows = conn.execute(
        "SELECT salon_id FROM profile.work_context WHERE master_id = %s ORDER BY salon_id",
        (master_id,),
    ).fetchall()
    assert [row[0] for row in rows] == sorted([salon_a, salon_b])


async def test_resolve_salon_by_start_code(
    store: PostgresProfileStore, conn: psycopg.Connection
) -> None:
    salon_id = _unique_salon(conn)
    code = conn.execute(
        "SELECT telegram_start_code FROM profile.salon WHERE salon_id = %s",
        (salon_id,),
    ).fetchone()
    assert code is not None
    salon = await store.resolve_salon_by_start_code(code[0])
    assert salon is not None
    assert salon.salon_id == salon_id
    assert salon.name == "Contract Test Salon"
    assert salon.tz == "Europe/Moscow"
    unknown = await store.resolve_salon_by_start_code(f"nope-{uuid.uuid4().hex[:8]}")
    assert unknown is None


async def test_update_dedup_first_and_second_sighting(
    conn: psycopg.Connection,
) -> None:
    """AC #7 / AD-12: first sighting True, replay False; rows land in the table."""
    dedup = PostgresUpdateDedup(conn)
    update_id = randrange(10**12, 10**15)
    assert await dedup.record_update_id(update_id) is True
    assert await dedup.record_update_id(update_id) is False
    rows = conn.execute(
        "SELECT count(*) FROM messaging.telegram_update_dedup WHERE update_id = %s",
        (update_id,),
    ).fetchone()
    assert rows is not None and rows[0] == 1


def test_migration_idempotent_after_0002(conn: psycopg.Connection) -> None:
    """Re-running the runner applies nothing — including after 0002."""
    assert apply_pending(conn) == []
    recorded = {
        row[0]
        for row in conn.execute("SELECT filename FROM schema_migrations").fetchall()
    }
    assert "0002_profile_master_tables.sql" in recorded
