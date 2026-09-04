#!/bin/sh
# Creates the throwaway DB-backed-test database next to the dev one
# (Story 1.1c review finding: TEST_DATABASE_URL must not alias the
# persistent dev DB). Runs automatically on a fresh postgres_data volume;
# for an existing volume run once:
#   docker compose exec postgres createdb -U zabota zabota_test
set -e

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres \
  -c "CREATE DATABASE ${POSTGRES_DB}_test"
