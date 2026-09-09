#!/usr/bin/env bash
# Sourced by the official Apache Hop container entrypoint before project/environment registration.
# Generates an ephemeral Hop environment configuration from runtime PostgreSQL settings.
set -euo pipefail

: "${POSTGRES_HOST:=postgres}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=etl_audit}"
: "${POSTGRES_USER:=etl_user}"
: "${POSTGRES_PASSWORD:=synthetic-dev-password}"
: "${HOP_ENVIRONMENT_NAME:=runtime}"

json_escape() {
  local value="${1-}"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  value="${value//$'\r'/\\r}"
  value="${value//$'\t'/\\t}"
  printf '%s' "${value}"
}

runtime_config="/tmp/enterprise-etl-runtime-config.json"

cat > "${runtime_config}" <<EOF
{
  "variables": [
    {
      "name": "POSTGRES_HOST",
      "value": "$(json_escape "${POSTGRES_HOST}")",
      "description": "Runtime PostgreSQL host"
    },
    {
      "name": "POSTGRES_PORT",
      "value": "$(json_escape "${POSTGRES_PORT}")",
      "description": "Runtime PostgreSQL port"
    },
    {
      "name": "POSTGRES_DB",
      "value": "$(json_escape "${POSTGRES_DB}")",
      "description": "Runtime PostgreSQL database"
    },
    {
      "name": "POSTGRES_USER",
      "value": "$(json_escape "${POSTGRES_USER}")",
      "description": "Runtime PostgreSQL user"
    },
    {
      "name": "POSTGRES_PASSWORD",
      "value": "$(json_escape "${POSTGRES_PASSWORD}")",
      "description": "Runtime PostgreSQL credential"
    }
  ]
}
EOF

chmod 600 "${runtime_config}"
HOP_ENVIRONMENT_CONFIG_FILE_NAME_PATHS="${runtime_config}"
