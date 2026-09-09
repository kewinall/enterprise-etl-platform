#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOP_IMAGE="${HOP_IMAGE:-apache/hop:2.19.0}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:16-alpine}"
HOP_SMOKE_PORT="${HOP_SMOKE_PORT:-18181}"
RUN_SUFFIX="${GITHUB_RUN_ID:-local}-$$"
NETWORK_NAME="enterprise-etl-v03-${RUN_SUFFIX}"
POSTGRES_CONTAINER="enterprise-etl-postgres-${RUN_SUFFIX}"
HOP_CONTAINER="enterprise-etl-hop-${RUN_SUFFIX}"

POSTGRES_DB="etl_audit"
POSTGRES_USER="etl_user"
POSTGRES_PASSWORD="synthetic-ci-password"
HOP_USER="hop-smoke"
HOP_PASS="synthetic-hop-smoke-password"
RUN_ID="synthetic-ci-retry-run"
CORRELATION_ID="hop_synthetic_customer_daily:${RUN_ID}"

cleanup() {
  docker rm -f "${HOP_CONTAINER}" >/dev/null 2>&1 || true
  docker rm -f "${POSTGRES_CONTAINER}" >/dev/null 2>&1 || true
  docker network rm "${NETWORK_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker network create "${NETWORK_NAME}" >/dev/null

docker run -d \
  --name "${POSTGRES_CONTAINER}" \
  --network "${NETWORK_NAME}" \
  -e POSTGRES_DB="${POSTGRES_DB}" \
  -e POSTGRES_USER="${POSTGRES_USER}" \
  -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  -v "${ROOT_DIR}/postgres/init:/docker-entrypoint-initdb.d:ro" \
  "${POSTGRES_IMAGE}" >/dev/null

postgres_ready=0
for _ in $(seq 1 60); do
  if docker exec "${POSTGRES_CONTAINER}" \
      pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; then
    postgres_ready=1
    break
  fi
  sleep 2
done

if [[ "${postgres_ready}" -ne 1 ]]; then
  echo "PostgreSQL did not become ready."
  docker logs "${POSTGRES_CONTAINER}" || true
  exit 1
fi

docker run -d \
  --name "${HOP_CONTAINER}" \
  --network "${NETWORK_NAME}" \
  -p "127.0.0.1:${HOP_SMOKE_PORT}:8181" \
  -e HOP_PROJECT_FOLDER=/files/project \
  -e HOP_PROJECT_NAME=enterprise-etl \
  -e HOP_SERVER_HOSTNAME=0.0.0.0 \
  -e HOP_SERVER_PORT=8181 \
  -e HOP_SERVER_USER="${HOP_USER}" \
  -e HOP_SERVER_PASS="${HOP_PASS}" \
  -e HOP_LOG_LEVEL=Basic \
  -e POSTGRES_HOST="${POSTGRES_CONTAINER}" \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB="${POSTGRES_DB}" \
  -e POSTGRES_USER="${POSTGRES_USER}" \
  -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  -v "${ROOT_DIR}/hop/projects/enterprise-etl:/files/project:ro" \
  "${HOP_IMAGE}" >/dev/null

status_url="http://127.0.0.1:${HOP_SMOKE_PORT}/hop/status/?json=Y"
hop_ready=0
for _ in $(seq 1 60); do
  if curl --fail --silent \
      --user "${HOP_USER}:${HOP_PASS}" \
      "${status_url}" >/dev/null; then
    hop_ready=1
    break
  fi
  sleep 2
done

if [[ "${hop_ready}" -ne 1 ]]; then
  echo "Hop Server did not become ready."
  docker logs "${HOP_CONTAINER}" || true
  exit 1
fi

hop_exec() {
  local pipeline_file="$1"
  shift
  local pipeline_path='${PROJECT_HOME}/pipelines/'"${pipeline_file}"
  local response_file
  response_file="$(mktemp)"

  local curl_args=(
    --silent
    --show-error
    --output "${response_file}"
    --write-out "%{http_code}"
    --user "${HOP_USER}:${HOP_PASS}"
    --get "http://127.0.0.1:${HOP_SMOKE_PORT}/hop/execPipeline"
    --data-urlencode "pipeline=${pipeline_path}"
    --data-urlencode "runConfig=local"
    --data-urlencode "level=Basic"
    --data-urlencode "json=Y"
  )

  local item
  for item in "$@"; do
    curl_args+=(--data-urlencode "${item}")
  done

  local http_code
  http_code="$(curl "${curl_args[@]}")"
  local response
  response="$(cat "${response_file}")"
  rm -f "${response_file}"

  if [[ "${http_code}" != "200" ]]; then
    echo "Hop pipeline ${pipeline_file} returned HTTP ${http_code}."
    echo "Response:"
    printf '%s\n' "${response}"
    echo "Hop Server logs:"
    docker logs "${HOP_CONTAINER}" || true
    exit 1
  fi

  printf '%s' "${response}" | python -c '
import json
import sys
payload = json.load(sys.stdin)
if str(payload.get("result", "")).upper() != "OK":
    raise SystemExit(f"Hop execution failed: {payload}")
'
}

common_attempt_1=(
  "RUN_ENV=TEST"
  "RUN_ID=${RUN_ID}"
  "ATTEMPT_NUMBER=1"
  "CORRELATION_ID=${CORRELATION_ID}"
  "TRIGGER_TYPE=CI"
)

hop_exec "audit_execution_start.hpl" "${common_attempt_1[@]}"
hop_exec "audit_execution_finalize.hpl" \
  "RUN_ENV=TEST" \
  "RUN_ID=${RUN_ID}" \
  "ATTEMPT_NUMBER=1" \
  "FINAL_STATUS=FAILED" \
  "RECORDS_READ=0" \
  "RECORDS_WRITTEN=0" \
  "ERROR_MESSAGE=synthetic retry validation"

common_attempt_2=(
  "RUN_ENV=TEST"
  "RUN_ID=${RUN_ID}"
  "ATTEMPT_NUMBER=2"
  "CORRELATION_ID=${CORRELATION_ID}"
  "TRIGGER_TYPE=CI"
)

hop_exec "audit_execution_start.hpl" "${common_attempt_2[@]}"
hop_exec "synthetic_customer_daily.hpl" \
  "RUN_ENV=TEST" \
  "RUN_ID=${RUN_ID}" \
  "ATTEMPT_NUMBER=2" \
  "CORRELATION_ID=${CORRELATION_ID}"
hop_exec "audit_execution_finalize.hpl" \
  "RUN_ENV=TEST" \
  "RUN_ID=${RUN_ID}" \
  "ATTEMPT_NUMBER=2" \
  "FINAL_STATUS=SUCCESS" \
  "RECORDS_READ=3" \
  "RECORDS_WRITTEN=3" \
  "ERROR_MESSAGE="

psql_query() {
  docker exec "${POSTGRES_CONTAINER}" \
    psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Atc "$1"
}

attempt_states="$(
  psql_query "
    SELECT string_agg(
      attempt_number::text || ':' || status || ':' || records_written::text || ':' || COALESCE(error_message, ''),
      ',' ORDER BY attempt_number
    )
    FROM etl_audit.etl_execution_log
    WHERE run_id = '${RUN_ID}';
  "
)"
expected_states="1:FAILED:0:synthetic retry validation,2:SUCCESS:3:"
if [[ "${attempt_states}" != "${expected_states}" ]]; then
  echo "Unexpected execution states: ${attempt_states}"
  exit 1
fi

event_states="$(
  psql_query "
    SELECT string_agg(e.event_type, ',' ORDER BY e.event_id)
    FROM etl_audit.etl_execution_event e
    JOIN etl_audit.etl_execution_log l ON l.execution_id = e.execution_id
    WHERE l.run_id = '${RUN_ID}';
  "
)"
if [[ "${event_states}" != "STARTED,FAILED,STARTED,SUCCEEDED" ]]; then
  echo "Unexpected lifecycle events: ${event_states}"
  exit 1
fi

target_count="$(
  psql_query "
    SELECT count(*)
    FROM etl_data.synthetic_customer_daily
    WHERE run_id = '${RUN_ID}' AND attempt_number = 2;
  "
)"
if [[ "${target_count}" != "3" ]]; then
  echo "Expected 3 persisted synthetic rows, got ${target_count}."
  exit 1
fi

target_sum="$(
  psql_query "
    SELECT to_char(sum(amount), 'FM999999990.00')
    FROM etl_data.synthetic_customer_daily
    WHERE run_id = '${RUN_ID}' AND attempt_number = 2;
  "
)"
if [[ "${target_sum}" != "361.50" ]]; then
  echo "Unexpected persisted amount sum: ${target_sum}"
  exit 1
fi

unfinished_count="$(
  psql_query "
    SELECT count(*)
    FROM etl_audit.etl_execution_log
    WHERE run_id = '${RUN_ID}' AND finished_at IS NULL;
  "
)"
if [[ "${unfinished_count}" != "0" ]]; then
  echo "Expected all smoke-test attempts to be finalized."
  exit 1
fi

echo "v0.3 PostgreSQL audit/retry/persistence lifecycle smoke test passed."
