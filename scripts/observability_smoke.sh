#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_SUFFIX="${GITHUB_RUN_ID:-local}-$$"
NETWORK_NAME="enterprise-etl-observability-${RUN_SUFFIX}"
POSTGRES_CONTAINER="etl-observability-postgres-${RUN_SUFFIX}"
EXPORTER_CONTAINER="etl-observability-exporter-${RUN_SUFFIX}"
PROMETHEUS_CONTAINER="etl-observability-prometheus-${RUN_SUFFIX}"
ALERTMANAGER_CONTAINER="etl-observability-alertmanager-${RUN_SUFFIX}"
GRAFANA_CONTAINER="etl-observability-grafana-${RUN_SUFFIX}"

POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:16-alpine}"
SQL_EXPORTER_IMAGE="${SQL_EXPORTER_IMAGE:-burningalchemist/sql_exporter:0.24.8}"
PROMETHEUS_IMAGE="${PROMETHEUS_IMAGE:-prom/prometheus:v3.14.0}"
ALERTMANAGER_IMAGE="${ALERTMANAGER_IMAGE:-prom/alertmanager:v0.34.0}"
GRAFANA_IMAGE="${GRAFANA_IMAGE:-grafana/grafana:13.2.1}"

POSTGRES_DB="etl_audit"
POSTGRES_USER="etl_user"
POSTGRES_PASSWORD="synthetic-dev-password"
GRAFANA_PASSWORD="synthetic-grafana-password"

cleanup() {
  docker rm -f     "${GRAFANA_CONTAINER}"     "${PROMETHEUS_CONTAINER}"     "${ALERTMANAGER_CONTAINER}"     "${EXPORTER_CONTAINER}"     "${POSTGRES_CONTAINER}" >/dev/null 2>&1 || true
  docker network rm "${NETWORK_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker network create "${NETWORK_NAME}" >/dev/null

docker run -d   --name "${POSTGRES_CONTAINER}"   --network "${NETWORK_NAME}"   --network-alias postgres   -e POSTGRES_DB="${POSTGRES_DB}"   -e POSTGRES_USER="${POSTGRES_USER}"   -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"   -v "${ROOT_DIR}/postgres/init:/docker-entrypoint-initdb.d:ro"   "${POSTGRES_IMAGE}" >/dev/null

for _ in $(seq 1 60); do
  if docker exec "${POSTGRES_CONTAINER}"       pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

docker exec -i "${POSTGRES_CONTAINER}"   psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null <<'SQL'
INSERT INTO etl_audit.etl_execution_log (
    pipeline_name, environment_name, run_id, status,
    started_at, finished_at, records_read, records_written,
    error_message, correlation_id, attempt_number, trigger_type
)
VALUES
(
    'synthetic_customer_daily', 'TEST', 'observability-run-success-1', 'SUCCESS',
    CURRENT_TIMESTAMP - INTERVAL '12 minutes',
    CURRENT_TIMESTAMP - INTERVAL '11 minutes',
    3, 3, NULL,
    'synthetic_customer_daily:observability-success-1', 1, 'CI'
),
(
    'synthetic_customer_daily', 'TEST', 'observability-run-failed-1', 'FAILED',
    CURRENT_TIMESTAMP - INTERVAL '10 minutes',
    CURRENT_TIMESTAMP - INTERVAL '9 minutes',
    3, 0, 'synthetic observability failure',
    'synthetic_customer_daily:observability-retry', 1, 'CI'
),
(
    'synthetic_customer_daily', 'TEST', 'observability-run-success-2', 'SUCCESS',
    CURRENT_TIMESTAMP - INTERVAL '8 minutes',
    CURRENT_TIMESTAMP - INTERVAL '7 minutes',
    3, 3, NULL,
    'synthetic_customer_daily:observability-retry', 2, 'CI'
),
(
    'synthetic_customer_daily', 'TEST', 'observability-run-stale-1', 'RUNNING',
    CURRENT_TIMESTAMP - INTERVAL '45 minutes',
    NULL,
    0, 0, NULL,
    'synthetic_customer_daily:observability-stale', 1, 'CI'
);
SQL

docker run --rm   --entrypoint /bin/promtool   -v "${ROOT_DIR}/monitoring/prometheus:/etc/prometheus:ro"   "${PROMETHEUS_IMAGE}"   check config /etc/prometheus/prometheus.yml >/dev/null

docker run -d   --name "${EXPORTER_CONTAINER}"   --network "${NETWORK_NAME}"   --network-alias sql-exporter   -p "127.0.0.1:19399:9399"   -v "${ROOT_DIR}/monitoring/sql-exporter:/config:ro"   "${SQL_EXPORTER_IMAGE}"   -config.file=/config/sql_exporter.yml >/dev/null

docker run -d   --name "${ALERTMANAGER_CONTAINER}"   --network "${NETWORK_NAME}"   --network-alias alertmanager   -p "127.0.0.1:19093:9093"   -v "${ROOT_DIR}/monitoring/alertmanager:/etc/alertmanager:ro"   "${ALERTMANAGER_IMAGE}"   --config.file=/etc/alertmanager/alertmanager.yml >/dev/null

docker run -d   --name "${PROMETHEUS_CONTAINER}"   --network "${NETWORK_NAME}"   --network-alias prometheus   -p "127.0.0.1:19090:9090"   -v "${ROOT_DIR}/monitoring/prometheus:/etc/prometheus:ro"   "${PROMETHEUS_IMAGE}"   --config.file=/etc/prometheus/prometheus.yml   --storage.tsdb.path=/prometheus >/dev/null

docker run -d   --name "${GRAFANA_CONTAINER}"   --network "${NETWORK_NAME}"   --network-alias grafana   -p "127.0.0.1:13000:3000"   -e GF_SECURITY_ADMIN_USER=admin   -e GF_SECURITY_ADMIN_PASSWORD="${GRAFANA_PASSWORD}"   -e GF_AUTH_ANONYMOUS_ENABLED=false   -v "${ROOT_DIR}/monitoring/grafana/provisioning:/etc/grafana/provisioning:ro"   -v "${ROOT_DIR}/monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro"   "${GRAFANA_IMAGE}" >/dev/null

wait_http() {
  local url="$1"
  local description="$2"
  for _ in $(seq 1 90); do
    if curl --fail --silent "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  echo "${description} did not become ready: ${url}"
  docker logs "${EXPORTER_CONTAINER}" || true
  docker logs "${PROMETHEUS_CONTAINER}" || true
  docker logs "${ALERTMANAGER_CONTAINER}" || true
  docker logs "${GRAFANA_CONTAINER}" || true
  return 1
}

wait_http "http://127.0.0.1:19399/metrics" "SQL Exporter"
wait_http "http://127.0.0.1:19093/-/ready" "Alertmanager"
wait_http "http://127.0.0.1:19090/-/ready" "Prometheus"

for _ in $(seq 1 30); do
  if curl --fail --silent       --user "admin:${GRAFANA_PASSWORD}"       "http://127.0.0.1:13000/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

metrics="$(curl --fail --silent http://127.0.0.1:19399/metrics)"
for metric in   etl_pipeline_run_total   etl_pipeline_retry_total   etl_records_written_total   etl_running_stale_total   etl_last_success_timestamp_seconds   etl_pipeline_duration_seconds   etl_pipeline_duration_p95_seconds; do
  if ! grep -q "^# HELP ${metric} " <<<"${metrics}"; then
    echo "Missing exporter metric: ${metric}"
    exit 1
  fi
done

query_result="$(
  curl --fail --silent --get     --data-urlencode 'query=etl_pipeline_run_total{pipeline_name="synthetic_customer_daily",environment_name="TEST"}'     http://127.0.0.1:19090/api/v1/query
)"
printf '%s' "${query_result}" | python -c '
import json, sys
payload = json.load(sys.stdin)
assert payload["status"] == "success", payload
assert payload["data"]["result"], payload
'

rules="$(curl --fail --silent http://127.0.0.1:19090/api/v1/rules)"
printf '%s' "${rules}" | python -c '
import json, sys
payload = json.load(sys.stdin)
names = {
    rule["name"]
    for group in payload["data"]["groups"]
    for rule in group["rules"]
}
required = {
    "etl:slo_success_ratio",
    "etl:slo_error_ratio",
    "etl:slo_error_budget_remaining",
    "ETLPipelineSLOBreach",
    "ETLStaleRunningExecution",
    "ETLNoRecentSuccess",
}
missing = required - names
assert not missing, missing
'

alerts_ok=0
for _ in $(seq 1 20); do
  alerts="$(curl --fail --silent http://127.0.0.1:19090/api/v1/alerts)"
  if printf '%s' "${alerts}" | python -c '
import json, sys
payload = json.load(sys.stdin)
firing = {
    alert["labels"]["alertname"]
    for alert in payload["data"]["alerts"]
    if alert["state"] == "firing"
}
required = {"ETLPipelineSLOBreach", "ETLStaleRunningExecution"}
raise SystemExit(0 if required <= firing else 1)
'; then
    alerts_ok=1
    break
  fi
  sleep 2
done

if [[ "${alerts_ok}" -ne 1 ]]; then
  echo "Expected SLO and stale-execution alerts to be firing."
  curl --silent http://127.0.0.1:19090/api/v1/alerts || true
  exit 1
fi

grafana_search="$(
  curl --fail --silent     --user "admin:${GRAFANA_PASSWORD}"     --get --data-urlencode 'query=Enterprise ETL Operations'     http://127.0.0.1:13000/api/search
)"
printf '%s' "${grafana_search}" | python -c '
import json, sys
payload = json.load(sys.stdin)
assert any(item.get("uid") == "enterprise-etl-ops" for item in payload), payload
'

curl --fail --silent   --user "admin:${GRAFANA_PASSWORD}"   http://127.0.0.1:13000/api/datasources/uid/prometheus >/dev/null

echo "v0.5 Prometheus/Grafana/SLO/alert observability smoke test passed."
