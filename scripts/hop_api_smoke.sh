#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOP_IMAGE="${HOP_IMAGE:-apache/hop:2.19.0}"
HOP_SMOKE_PORT="${HOP_SMOKE_PORT:-18181}"
HOP_SMOKE_USER="hop-smoke"
HOP_SMOKE_PASS="synthetic-hop-smoke-password"
CONTAINER_NAME="enterprise-etl-hop-smoke-${GITHUB_RUN_ID:-local}-$$"

cleanup() {
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run -d   --name "${CONTAINER_NAME}"   -p "127.0.0.1:${HOP_SMOKE_PORT}:8181"   -e HOP_PROJECT_FOLDER=/files/project   -e HOP_PROJECT_NAME=enterprise-etl   -e HOP_SERVER_HOSTNAME=0.0.0.0   -e HOP_SERVER_PORT=8181   -e HOP_SERVER_USER="${HOP_SMOKE_USER}"   -e HOP_SERVER_PASS="${HOP_SMOKE_PASS}"   -e HOP_LOG_LEVEL=Basic   -v "${ROOT_DIR}/hop/projects/enterprise-etl:/files/project:ro"   "${HOP_IMAGE}" >/dev/null

status_url="http://127.0.0.1:${HOP_SMOKE_PORT}/hop/status/?json=Y"

ready=0
for _ in $(seq 1 60); do
  if curl --fail --silent       --user "${HOP_SMOKE_USER}:${HOP_SMOKE_PASS}"       "${status_url}" >/dev/null; then
    ready=1
    break
  fi
  sleep 2
done

if [[ "${ready}" -ne 1 ]]; then
  echo "Hop Server did not become ready."
  docker logs "${CONTAINER_NAME}" || true
  exit 1
fi

tmp_response="$(mktemp)"
http_code="$(
  curl --silent --show-error     --output "${tmp_response}"     --write-out '%{http_code}'     --user "${HOP_SMOKE_USER}:${HOP_SMOKE_PASS}"     --get "http://127.0.0.1:${HOP_SMOKE_PORT}/hop/execPipeline"     --data-urlencode 'pipeline=${PROJECT_HOME}/pipelines/synthetic_customer_daily.hpl'     --data-urlencode 'runConfig=local'     --data-urlencode 'level=Basic'     --data-urlencode 'json=Y'     --data-urlencode 'RUN_ENV=CI'
)"

response="$(cat "${tmp_response}")"
rm -f "${tmp_response}"

if [[ "${http_code}" != "200" ]]; then
  echo "Hop pipeline execution returned HTTP ${http_code}."
  echo "Response:"
  printf '%s\n' "${response}"
  echo "Hop Server logs:"
  docker logs "${CONTAINER_NAME}" || true
  exit 1
fi

printf '%s' "${response}" | python -c '
import json
import sys

payload = json.load(sys.stdin)
if str(payload.get("result", "")).upper() != "OK":
    raise SystemExit(f"Hop smoke test failed: {payload}")
print("Hop Server API smoke test passed.")
'
