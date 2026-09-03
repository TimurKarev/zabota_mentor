"""Minimal idempotent SQL migration runner (Story 1.1b).

Applies pending ``migrations/*.sql`` files in filename order, each inside its
own transaction, recording applied files in ``schema_migrations``. No
down-migrations — schema changes in this project are additive (see
``migrations/0001_config_and_audit_schemas.sql`` for the rationale).

Runnable as a module entry (``uv run python -m src.adapters.db.migrate``) and
importable from tests. Plain SQL, no Alembic: the architecture mandates no
migration tool, and the files stay parseable by the schema-ownership check
(``tests/unit/test_schema_ownership.py``).
"""

import os
import sys
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS_DIR = REPO_ROOT / "migrations"


def migration_files(migrations_dir: Path = MIGRATIONS_DIR) -> list[Path]:
    """Ordered ``*.sql`` files from the migrations directory."""
    return sorted(migrations_dir.glob("*.sql"))


def apply_pending(conn: psycopg.Connection, migrations_dir: Path = MIGRATIONS_DIR) -> list[str]:
    """Apply pending migrations, return the filenames applied (empty if none).

    Idempotent: files already recorded in ``schema_migrations`` are skipped.
    Each file runs in its own transaction; the recording insert commits with it.
    """
    applied: list[str] = []
    with conn.transaction():
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename   text        NOT NULL PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        rows = conn.execute(
            "SELECT filename FROM schema_migrations").fetchall()
    already = {row[0] for row in rows}
    for path in migration_files(migrations_dir):
        if path.name in already:
            continue
        with conn.transaction():
            conn.execute(path.read_text(encoding="utf-8"))
            conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES (%s)", (
                    path.name,)
            )
        applied.append(path.name)
    return applied


def main() -> int:
    """Entry point: apply pending migrations using ``DATABASE_URL``."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set — nothing to migrate.", file=sys.stderr)
        return 1
    with psycopg.connect(database_url) as conn:
        applied = apply_pending(conn)
    if applied:
        print(f"Applied {len(applied)} migration(s): {', '.join(applied)}")
    else:
        print("No pending migrations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
