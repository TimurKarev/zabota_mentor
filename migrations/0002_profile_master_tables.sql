-- 0002: profile master tables + messaging update dedup (Story 1.2; AD-13, AD-7, AD-12, AD-8).
--
-- Ownership: schema `profile` -> src.adapters.profile_store; schema `messaging` ->
-- src.adapters.messaging_store (enforced by tests/unit/test_schema_ownership.py).
--
-- Plain SQL, additive only, applied in one transaction by the runner (same
-- rules as 0001). Keep this file parseable by the schema-ownership regex
-- check: no /* */ block comments, no quoted identifiers.

CREATE SCHEMA IF NOT EXISTS profile;
CREATE SCHEMA IF NOT EXISTS messaging;

-- AD-13: one canonical master identity, owned by the `profile` module. The
-- psych profile is master-level (AD-7): no salon column here — salon scoping
-- lives on work_context (and later salon-scoped rows).
CREATE TABLE IF NOT EXISTS profile.master (
    master_id  uuid        NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- The anchor mapping (AD-13): chat_id <-> master_id. Everything downstream
-- keys off master_id, never chat_id.
CREATE TABLE IF NOT EXISTS profile.master_chat_map (
    chat_id    bigint      NOT NULL PRIMARY KEY,
    master_id  uuid        NOT NULL REFERENCES profile.master,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Salon-scoped work context (AD-7): one master, N salons. Every salon-scoped
-- domain row carries salon_id.
CREATE TABLE IF NOT EXISTS profile.work_context (
    master_id  uuid        NOT NULL,
    salon_id   text        NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (master_id, salon_id)
);

-- Salons known to the system; `telegram_start_code` is the deep-link payload
-- a master receives (`https://t.me/<bot>?start=<code>`). `tz` is an IANA name
-- (AD-8: static RU zones UTC+2..+12, NFR-F).
CREATE TABLE IF NOT EXISTS profile.salon (
    salon_id             text NOT NULL PRIMARY KEY,
    telegram_start_code  text NOT NULL UNIQUE,
    name                 text NOT NULL,
    tz                   text NOT NULL DEFAULT 'Europe/Moscow'
);

-- AD-12: durable update_id dedup for at-least-once Telegram delivery. The
-- table IS the dedup marker — insert-only, no UPDATE/DELETE needed; a retry
-- hits ON CONFLICT DO NOTHING (see src/adapters/messaging_store).
CREATE TABLE IF NOT EXISTS messaging.telegram_update_dedup (
    update_id    bigint      NOT NULL PRIMARY KEY,
    processed_at timestamptz NOT NULL DEFAULT now()
);

-- Dev seed: one salon so M0 deep links resolve end-to-end (`/start salon1`).
INSERT INTO profile.salon (salon_id, telegram_start_code, name)
VALUES ('dev-salon', 'salon1', 'Dev Salon')
ON CONFLICT (salon_id) DO NOTHING;
