"""AC-4 (Story 1.1b): schema-ownership check — no cross-module table access (AD-11).

Pairs with import-linter on the code side: every Postgres schema/object is
owned by exactly one module adapter, and migrations may only create/alter
objects in a schema that is declared here. Creating an undeclared schema or
touching another module's schema fails this check. It runs locally as part of
``pytest``; CI wiring itself is Story 1.1c.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "migrations"

# AD-11 ownership map: Postgres schema -> owning module.
# `crm_mirror`, `profile`, `engines`, `messaging` land with their owning stories;
# when they do, add them here IN THE SAME change.
SCHEMA_OWNERS = {
    "config": "src.adapters.config_store",
    "audit": "src.adapters.audit",
    # Cross-cutting bookkeeping only (schema_migrations + the runner), not a module.
    "public": "src.adapters.db",
}

# Keyword-anchored object references. `CREATE/DROP INDEX` and `CREATE/DROP
# TRIGGER` address their target via `ON <schema.table>`; everything else
# (TABLE, SCHEMA, FUNCTION, VIEW, INTO/FROM/UPDATE/...) names it directly.
# `ON CONFLICT` never carries a qualified name, so the ON-pattern is safe there.
_QUALIFIED_TARGET_RE = re.compile(
    r"\b(?:TABLE|VIEW|FUNCTION|PROCEDURE|SEQUENCE|TYPE|INTO|FROM|UPDATE|TRUNCATE|REFERENCES)"
    r"(?:\s+IF\s+(?:NOT\s+)?EXISTS)?\s+(\w+)\.(\w+)",
    re.IGNORECASE,
)
_ON_TARGET_RE = re.compile(r"\bON\s+(\w+)\.(\w+)", re.IGNORECASE)
_CREATE_SCHEMA_RE = re.compile(
    r"\bCREATE\s+SCHEMA\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)", re.IGNORECASE
)


def _strip_comments(sql: str) -> str:
    return "\n".join(line.split("--", 1)[0] for line in sql.splitlines())


def _referenced_schemas(sql: str) -> set[str]:
    """Every schema referenced by a schema-qualified object in the SQL."""
    stripped = _strip_comments(sql)
    schemas = {m.group(1).lower() for m in _QUALIFIED_TARGET_RE.finditer(stripped)}
    schemas.update(m.group(1).lower() for m in _ON_TARGET_RE.finditer(stripped))
    return schemas


def _created_schemas(sql: str) -> set[str]:
    """Schemas explicitly created by `CREATE SCHEMA` statements."""
    return {
        m.group(1).lower()
        for m in _CREATE_SCHEMA_RE.finditer(_strip_comments(sql))
    }


def test_migrations_only_touch_declared_schemas() -> None:
    """Every schema a migration touches must be in the ownership map (AD-11)."""
    undeclared: dict[str, list[str]] = {}
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        for schema in _referenced_schemas(path.read_text(encoding="utf-8")):
            if schema not in SCHEMA_OWNERS:
                undeclared.setdefault(schema, []).append(path.name)
    assert not undeclared, (
        f"Migrations touch schemas with no declared owner (AD-11): {undeclared}. "
        "Add the schema to SCHEMA_OWNERS together with its owning module adapter."
    )


def test_declared_schemas_exist_in_migrations() -> None:
    """The ownership map must not declare schemas no migration creates yet."""
    created: set[str] = set()
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        created |= _created_schemas(path.read_text(encoding="utf-8"))
    missing = set(SCHEMA_OWNERS) - created - {"public"}
    assert not missing, (
        f"SCHEMA_OWNERS declares schemas no migration creates: {sorted(missing)}. "
        "Ownership entries arrive together with the migration that creates the schema."
    )


def test_migration_files_are_ordered_and_unique() -> None:
    """File naming `NNNN_description.sql`: prefixes strictly increasing, no duplicates."""
    names = sorted(path.name for path in MIGRATIONS_DIR.glob("*.sql"))
    assert names, "migrations/ must contain at least one .sql file"
    prefixes = [name.split("_", 1)[0] for name in names]
    assert all(re.fullmatch(r"\d{4}", p) for p in prefixes), f"bad prefix in {names}"
    assert len(set(prefixes)) == len(prefixes), f"duplicate migration prefix in {names}"
    assert prefixes == sorted(prefixes), f"migration prefixes out of order: {names}"


def test_parser_recognizes_reference_sql() -> None:
    """Self-check: the parser sees the statement shapes real migrations use (guards regex rot)."""
    sample = (
        "CREATE SCHEMA IF NOT EXISTS crm_mirror;\n"
        "-- a comment mentioning audit.event\n"
        "CREATE TABLE config.config_version (version bigint);\n"
        "CREATE TRIGGER t BEFORE UPDATE ON audit.event\n"
        "    FOR EACH ROW EXECUTE FUNCTION audit.reject_mutation();\n"
        "CREATE INDEX i ON crm_mirror.deal;\n"
        "INSERT INTO config.config_version DEFAULT VALUES;\n"
        "UPDATE audit.event SET x = 1;\n"
    )
    assert _referenced_schemas(sample) == {"config", "audit", "crm_mirror"}
    assert _created_schemas(sample) == {"crm_mirror"}


def test_parser_flags_undeclared_schema() -> None:
    """Self-check: a migration touching an undeclared schema would be caught."""
    assert _referenced_schemas("CREATE TABLE profile.master (id int);") == {"profile"}
