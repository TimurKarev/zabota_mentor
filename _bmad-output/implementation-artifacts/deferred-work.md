# Deferred Work Ledger

Items deferred from code reviews, retrospectives, and other BMAD workflows.
Each entry includes a one-line reason for deferral to help future reviews.

## Deferred from: code review of 1-1b-versioned-config-store-audit-log (2026-09-03)

- TOCTOU / no advisory lock in migration runner [src/adapters/db/migrate.py:36-56] — The `already` set is read outside the apply loop; concurrent runs can double-apply. Spec requires idempotency (re-runs safe) but not concurrent-run safety. Add pg_advisory_lock when concurrent starts become a real scenario.
- schema_migrations DDL duplicated between runner and migration 0001 [src/adapters/db/migrate.py:37-44, migrations/0001_config_and_audit_schemas.sql:16-19] — Both create the same table with IF NOT EXISTS. Definitions are identical today; drift risk if either changes. Consolidate when schema_migrations evolves.
- _strip_comments does not handle block comments (/* ... */) [tests/unit/test_schema_ownership.py:41-42] — Naive split on `--` breaks on string literals containing `--` and misses block comments. No current migration triggers this. Improve when future migrations need it.
- Schema-ownership parser misses quoted identifiers [tests/unit/test_schema_ownership.py:30-38] — Regexes use \w+; quoted identifiers like "Config"."ConfigVersion" bypass the check. No current migration uses quoted identifiers. Improve when needed.
- Schema-ownership parser does not detect DROP SCHEMA or ALTER SCHEMA [tests/unit/test_schema_ownership.py:36-38] — Only CREATE SCHEMA is detected. Spec says "additive only: no down-migrations." DROP/ALTER SCHEMA is out of scope. Add when non-additive migrations appear.
- No max-length boundary on author, justification, kind, scope [src/adapters/config_store/models.py:24-29, src/adapters/audit/__init__.py:25-30] — _non_empty only checks emptiness, no max_length. Potential memory/DoS vector at the editing boundary. The boundary is human-driven (authorized config editors). Add max_length when the threat model requires it.
- _ON_TARGET_RE false positives on JOIN ... ON schema.column [tests/unit/test_schema_ownership.py:35] — The regex matches any ON schema.identifier, not just CREATE TRIGGER/INDEX contexts. No current migration has JOIN clauses. Tighten the regex when JOIN migrations appear.
- Schema-ownership check does not enforce per-migration ownership [tests/unit/test_schema_ownership.py:61-71] — Only global schema declaration is checked, not per-migration authorization. Moot with one migration and one owner per schema. Add per-migration ownership when multiple migrations touch the same schema.
