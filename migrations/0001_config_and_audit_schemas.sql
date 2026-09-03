-- 0001: config + audit schemas (Story 1.1b; AD-6, AD-11, AD-8).
--
-- Ownership: schema `config` -> src.adapters.config_store; schema `audit` ->
-- src.adapters.audit; `schema_migrations` bookkeeping -> src.adapters.db
-- (enforced by tests/unit/test_schema_ownership.py).
--
-- Plain SQL migrations, applied in order by src/adapters/db/migrate.py.
-- Additive only: no down-migrations (AD-6 insert-only culture applies to
-- structure too where practical). Each file is applied inside one transaction
-- by the runner — files carry no BEGIN/COMMIT of their own.

CREATE SCHEMA IF NOT EXISTS config;
CREATE SCHEMA IF NOT EXISTS audit;

-- Bookkeeping for the migration runner (applied files, in order).
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename  text        NOT NULL PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);

-- AD-6: insert-only versioned config rows. Immutable after insert: no UPDATE,
-- no DELETE (trigger guard below). Activating a prior version is itself an
-- INSERT of a new row — rollback is an insert, which satisfies FR-14.1 (< 5 min)
-- mechanically.
CREATE TABLE IF NOT EXISTS config.config_version (
    version    bigint        NOT NULL,
    kind       text          NOT NULL DEFAULT 'params',
    scope      text          NOT NULL DEFAULT 'global',
    params     jsonb         NOT NULL,
    author     text          NOT NULL,
    created_at timestamptz   NOT NULL DEFAULT now(),
    valid_from timestamptz   NOT NULL,
    PRIMARY KEY (kind, scope, version)
);

CREATE INDEX IF NOT EXISTS config_version_active_lookup
    ON config.config_version (kind, scope, valid_from);

-- Belt-and-braces immutability: the store API exposes no update/delete, and the
-- database rejects them regardless of role (the trigger survives even
-- superuser/migration roles; permissions alone would not).
CREATE OR REPLACE FUNCTION config.reject_mutation() RETURNS trigger
    LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'config.config_version is insert-only (AD-6): % is not allowed', TG_OP;
END;
$$;

DROP TRIGGER IF EXISTS config_version_insert_only ON config.config_version;
CREATE TRIGGER config_version_insert_only
    BEFORE UPDATE OR DELETE ON config.config_version
    FOR EACH ROW EXECUTE FUNCTION config.reject_mutation();

DROP TRIGGER IF EXISTS config_version_no_truncate ON config.config_version;
CREATE TRIGGER config_version_no_truncate
    BEFORE TRUNCATE ON config.config_version
    FOR EACH STATEMENT EXECUTE FUNCTION config.reject_mutation();

-- AD-11 / FR-14.2: append-only audit trail. Every significant decision carries
-- a justification and its inputs. salon_id is NULL for global events (e.g.
-- config changes); salon-scoped events start with Story 1.3.
CREATE TABLE IF NOT EXISTS audit.event (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_type   text        NOT NULL,
    actor        text        NOT NULL,
    subject      jsonb       NOT NULL,
    inputs       jsonb       NOT NULL,
    justification text       NOT NULL,
    salon_id     text        NULL,
    occurred_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS event_occurred_at ON audit.event (occurred_at);

CREATE OR REPLACE FUNCTION audit.reject_mutation() RETURNS trigger
    LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'audit.event is append-only (AD-11): % is not allowed', TG_OP;
END;
$$;

DROP TRIGGER IF EXISTS event_append_only ON audit.event;
CREATE TRIGGER event_append_only
    BEFORE UPDATE OR DELETE ON audit.event
    FOR EACH ROW EXECUTE FUNCTION audit.reject_mutation();

DROP TRIGGER IF EXISTS event_no_truncate ON audit.event;
CREATE TRIGGER event_no_truncate
    BEFORE TRUNCATE ON audit.event
    FOR EACH STATEMENT EXECUTE FUNCTION audit.reject_mutation();

-- Seed the baseline params version (kind='params', scope='global', empty
-- params) so later stories always resolve an active version. Deliberately
-- empty of behavioral values — those land with their owning stories (7.5b).
INSERT INTO config.config_version (version, kind, scope, params, author, valid_from)
VALUES (1, 'params', 'global', '{}'::jsonb, 'system', '1970-01-01T00:00:00+00:00')
ON CONFLICT (kind, scope, version) DO NOTHING;
