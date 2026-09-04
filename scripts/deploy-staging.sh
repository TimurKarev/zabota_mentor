#!/bin/sh
# Deploy staging: sync code to the VM, rebuild the image, restart, migrate.
# Run from the repo root after the change is merged to main:
#   ./scripts/deploy-staging.sh
#
# What it does NOT do: push git, touch the server-side .env (bot token and
# DB password live only on the VM), or reset the database — postgres/redis
# containers and their volumes are preserved across restarts.
#
# Override host/user/key via env vars if the VM changes:
#   STAGING_HOST=... STAGING_USER=... STAGING_KEY=... ./scripts/deploy-staging.sh
set -eu

STAGING_HOST="${STAGING_HOST:-158.160.146.121}"
STAGING_USER="${STAGING_USER:-zabota_admin}"
STAGING_KEY="${STAGING_KEY:-$HOME/.ssh/zabota_staging}"
STAGING_DIR="${STAGING_DIR:-zabota_mentor}"

SSH="ssh -i ${STAGING_KEY} -o BatchMode=yes ${STAGING_USER}@${STAGING_HOST}"

echo "==> 1/3 Syncing code to ${STAGING_USER}@${STAGING_HOST}:~/${STAGING_DIR}"
rsync -az --delete -e "ssh -i ${STAGING_KEY}" \
  --exclude '.git' --exclude '.venv' --exclude '__pycache__' --exclude '_bmad' \
  --exclude '_bmad-output' --exclude '.env' --exclude 'docs' --exclude 'tests' \
  --exclude '.claude' --exclude '.python-version' \
  src migrations pyproject.toml uv.lock Dockerfile .dockerignore \
  docker-compose.staging.yml \
  "${STAGING_USER}@${STAGING_HOST}:${STAGING_DIR}/"

echo "==> 2/3 Rebuilding image and restarting (postgres/redis untouched)"
$SSH "cd ~/${STAGING_DIR} && \
  docker compose -f docker-compose.staging.yml up -d --build"

echo "==> 3/3 Running migrations (no-op when none are new)"
$SSH "cd ~/${STAGING_DIR} && \
  docker compose -f docker-compose.staging.yml run --rm app \
  python -m src.adapters.db.migrate"

echo "==> Status"
$SSH "cd ~/${STAGING_DIR} && \
  docker compose -f docker-compose.staging.yml ps --format \
  'table {{.Service}}\t{{.Status}}' && curl -s http://127.0.0.1:8000/health && echo"

echo "Staging deploy complete."
