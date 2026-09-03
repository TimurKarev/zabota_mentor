"""DB-backed tests for the config store + audit log (Story 1.1b, AC-1..AC-5).

Gated on ``TEST_DATABASE_URL`` (PostgreSQL 17): without it they skip with a
visible reason — the unit layer stays fully green without Docker. CI provides
the service from Story 1.1c; locally, see README for the throwaway one-liner.
"""

import os
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import psycopg
import pytest

from src.adapters.audit import AuditWriter
from src.adapters.config_store import PostgresConfigStore
from src.adapters.db.migrate import apply_pending

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is not set — DB-backed tests need a PostgreSQL 17 "
    "(see README: docker run --rm -e POSTGRES_PASSWORD=... -p 5432:5432 postgres:17)",
)

NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)


@pytest.fixture
def conn() -> Iterator[psycopg.Connection]:
    """Connection with migrations applied; the runner is idempotent per test."""
    with psycopg.connect(TEST_DATABASE_URL) as connection:
        apply_pending(connection)
        yield connection


@pytest.fixture
def store(conn: psycopg.Connection) -> PostgresConfigStore:
    return PostgresConfigStore(conn)


def _unique_scope() -> str:
    """Isolation without TRUNCATE: each test writes to its own scope."""
    return f"test-{uuid.uuid4().hex[:12]}"


def test_insert_then_read_back_by_version(
    store: PostgresConfigStore, conn: psycopg.Connection
) -> None:
    scope = _unique_scope()
    inserted = store.insert(
        {"alpha": 0.5}, author="timur", justification="initial", valid_from=NOW, scope=scope
    )
    assert inserted.version == 1
    read_back = store.get(1, scope=scope)
    assert read_back is not None
    assert read_back.params == {"alpha": 0.5}
    assert read_back.author == "timur"
    assert read_back.valid_from == NOW


def test_config_version_rejects_update_and_delete(conn: psycopg.Connection) -> None:
    """AC-1: immutability enforced by the database, not just by convention."""
    scope = _unique_scope()
    conn.execute(
        "INSERT INTO config.config_version (version, kind, scope, params, author, valid_from)"
        " VALUES (1, 'params', %s, '{}', 'test', now())",
        (scope,),
    )
    # Each probe runs in its own savepoint: the expected failure aborts the
    # enclosing transaction, which psycopg rolls back to the savepoint.
    with pytest.raises(psycopg.errors.RaiseException, match="insert-only"), conn.transaction():
        conn.execute(
            "UPDATE config.config_version SET author = 'tampered' WHERE scope = %s",
            (scope,),
        )
    with pytest.raises(psycopg.errors.RaiseException, match="insert-only"), conn.transaction():
        conn.execute("DELETE FROM config.config_version WHERE scope = %s", (scope,))


def test_audit_event_rejects_update_and_delete(conn: psycopg.Connection) -> None:
    """AC-2: append-only enforced at the database level."""
    writer = AuditWriter(conn)
    writer.append(
        event_type="test.probe",
        actor="test",
        subject={},
        inputs={},
        justification="immutability probe",
    )
    with pytest.raises(psycopg.errors.RaiseException, match="append-only"), conn.transaction():
        conn.execute("UPDATE audit.event SET actor = 'tampered'")
    with pytest.raises(psycopg.errors.RaiseException, match="append-only"), conn.transaction():
        conn.execute("DELETE FROM audit.event")


def test_active_resolution_and_activation_moves_it(
    store: PostgresConfigStore, conn: psycopg.Connection
) -> None:
    """AC-1: active() = greatest valid_from <= as_of; activation is a new row (AD-6)."""
    scope = _unique_scope()
    v1 = store.insert({}, author="timur", justification="v1", valid_from=NOW, scope=scope)
    v2 = store.insert(
        {"alpha": 0.9}, author="timur", justification="v2", valid_from=NOW + timedelta(days=1),
        scope=scope,
    )

    at_now = store.active(NOW + timedelta(hours=2), scope=scope)
    assert at_now is not None
    assert at_now.version == v1.version  # v2 not valid yet

    at_later = store.active(NOW + timedelta(days=2), scope=scope)
    assert at_later is not None
    assert at_later.version == v2.version

    # Rollback to v1 = INSERT a new row, never an UPDATE.
    v3 = store.activate(
        v1.version,
        author="timur",
        justification="rollback to v1",
        valid_from=NOW + timedelta(days=3),
        scope=scope,
    )
    assert v3.version == 3
    assert v3.params == v1.params
    after = store.active(NOW + timedelta(days=4), scope=scope)
    assert after is not None
    assert after.version == v3.version


def test_audit_rows_carry_justification_and_inputs(
    store: PostgresConfigStore, conn: psycopg.Connection
) -> None:
    """AC-3: config insert + activation both land as audit events."""
    scope = _unique_scope()
    store.insert(
        {"alpha": 0.5}, author="timur", justification="add alpha", valid_from=NOW, scope=scope
    )
    store.activate(
        1, author="timur", justification="rollback alpha", valid_from=NOW + timedelta(days=1),
        scope=scope,
    )
    rows = conn.execute(
        "SELECT event_type, actor, subject, inputs, justification, salon_id"
        " FROM audit.event WHERE subject->>'scope' = %s ORDER BY id",
        (scope,),
    ).fetchall()
    assert len(rows) == 2
    insert_row, activate_row = rows
    assert insert_row[0] == "config.insert"
    assert activate_row[0] == "config.activate"
    for row in rows:
        assert row[1] == "timur"
        assert row[4] in {"add alpha", "rollback alpha"}
        assert row[5] is None  # config events are global (AD-7)
    assert insert_row[3]["params"] == {"alpha": 0.5}
    assert activate_row[2]["prior_version"] == 1


def test_migration_runner_is_idempotent(conn: psycopg.Connection) -> None:
    """Second run applies nothing; bookkeeping matches the files on disk."""
    from src.adapters.db.migrate import migration_files

    applied_first = apply_pending(conn)
    applied_second = apply_pending(conn)
    recorded = {
        row[0]
        for row in conn.execute("SELECT filename FROM schema_migrations").fetchall()
    }
    # The connection fixture already migrated once, so the first re-run here is
    # also expected to be empty; the invariant is: never applies twice.
    assert applied_first == []
    assert applied_second == []
    assert recorded == {path.name for path in migration_files()}


def test_seeded_global_params_v1_is_active(store: PostgresConfigStore) -> None:
    """The migration seeds an empty-behavior baseline so active() always resolves."""
    active = store.active(NOW, kind="params", scope="global")
    assert active is not None
    assert active.version == 1
    assert active.params == {}
