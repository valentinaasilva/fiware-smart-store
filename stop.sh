#!/usr/bin/env bash
set -euo pipefail

QUIET="false"
if [[ "${1:-}" == "--quiet" ]]; then
  QUIET="true"
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="${ROOT_DIR}/.runtime"
PID_FILE="${RUNTIME_DIR}/app.pid"

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  COMPOSE_CMD=()
fi

if [[ -f "${PID_FILE}" ]]; then
  APP_PID="$(cat "${PID_FILE}")"
  if kill -0 "${APP_PID}" >/dev/null 2>&1; then
    [[ "${QUIET}" == "false" ]] && echo "[INFO] Stopping app (pid=${APP_PID})"
    kill "${APP_PID}" >/dev/null 2>&1 || true
    sleep 1
    kill -9 "${APP_PID}" >/dev/null 2>&1 || true
  fi
  rm -f "${PID_FILE}"
fi

# Best-effort cleanup if pid file is stale.
pkill -f "[p]ython.*app.py" >/dev/null 2>&1 || true

if [[ ${#COMPOSE_CMD[@]} -gt 0 ]]; then
  [[ "${QUIET}" == "false" ]] && echo "[INFO] Stopping Orion/Mongo/tutorial stack"
  "${COMPOSE_CMD[@]}" -f "${ROOT_DIR}/docker-compose.yml" down --remove-orphans
else
  [[ "${QUIET}" == "false" ]] && echo "[WARN] docker compose/docker-compose not available; only app process cleanup was attempted"
fi

[[ "${QUIET}" == "false" ]] && echo "[OK] Stop completed"
