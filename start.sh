#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="${ROOT_DIR}/.runtime"
PID_FILE="${RUNTIME_DIR}/app.pid"
LOG_FILE="${RUNTIME_DIR}/app.log"

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "[ERROR] docker compose/docker-compose is required" >&2
  exit 1
fi

mkdir -p "${RUNTIME_DIR}"

if [[ -x "${ROOT_DIR}/stop.sh" ]]; then
  echo "[INFO] Stopping previous app/containers if running"
  "${ROOT_DIR}/stop.sh" --quiet || true
fi

echo "[INFO] Starting Orion/Mongo/tutorial stack"
"${COMPOSE_CMD[@]}" -f "${ROOT_DIR}/docker-compose.yml" down --remove-orphans >/dev/null 2>&1 || true
"${COMPOSE_CMD[@]}" -f "${ROOT_DIR}/docker-compose.yml" up -d

ORION_PORT="${ORION_PORT:-1026}"
ORION_URL="${ORION_URL:-http://localhost:${ORION_PORT}}"
ORION_TIMEOUT="${ORION_TIMEOUT:-15}"
CALLBACK_BASE_URL="${CALLBACK_BASE_URL:-http://host.docker.internal:5000}"
PROVIDER_BASE_URL="${PROVIDER_BASE_URL:-${CALLBACK_BASE_URL}}"
WEATHER_PROVIDER_URL="${WEATHER_PROVIDER_URL:-${PROVIDER_BASE_URL}/providers/weather}"
TWEETS_PROVIDER_URL="${TWEETS_PROVIDER_URL:-${PROVIDER_BASE_URL}/providers/tweets}"
SEED_ON_START="${SEED_ON_START:-1}"

# Wait up to 60s for Orion health endpoint.
for i in $(seq 1 30); do
  if curl -fsS "${ORION_URL}/version" >/dev/null 2>&1; then
    echo "[INFO] Orion is reachable at ${ORION_URL}"
    break
  fi
  if [[ "$i" -eq 30 ]]; then
    echo "[WARN] Orion is not reachable after startup wait; app will boot with SQLite fallback"
    break
  fi
  sleep 2
done

PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python3"
fi

if [[ "${SEED_ON_START}" == "1" ]]; then
  echo "[INFO] Seeding Orion dataset (target=orion, clean=true)"
  (
    cd "${ROOT_DIR}"
    "${PYTHON_BIN}" scripts/load_test_data.py \
      --target orion \
      --orion-url "${ORION_URL}" \
      --clean
  )
  echo "[OK] Orion seed completed"
else
  echo "[WARN] Skipping Orion seed because SEED_ON_START=${SEED_ON_START}"
fi

# After seeding, Orion can be temporarily saturated. Wait until a lightweight
# entity query succeeds before booting Flask bootstrap calls.
for i in $(seq 1 20); do
  if curl -fsS "${ORION_URL}/v2/entities?limit=1" >/dev/null 2>&1; then
    echo "[INFO] Orion query API is responsive"
    break
  fi
  if [[ "$i" -eq 20 ]]; then
    echo "[WARN] Orion query API did not stabilize in time; continuing"
    break
  fi
  sleep 1
done

echo "[INFO] Starting Flask app in background"
(
  cd "${ROOT_DIR}"
  export ORION_URL
  export ORION_TIMEOUT
  export CALLBACK_BASE_URL
  export PROVIDER_BASE_URL
  export WEATHER_PROVIDER_URL
  export TWEETS_PROVIDER_URL
  nohup "${PYTHON_BIN}" app.py >"${LOG_FILE}" 2>&1 &
  echo $! >"${PID_FILE}"
)

APP_PID="$(cat "${PID_FILE}")"
if kill -0 "${APP_PID}" >/dev/null 2>&1; then
  echo "[OK] App started (pid=${APP_PID})"
  echo "[OK] Logs: ${LOG_FILE}"
  echo "[OK] UI: http://localhost:5000"
else
  echo "[ERROR] App failed to start. Check ${LOG_FILE}" >&2
  exit 1
fi
