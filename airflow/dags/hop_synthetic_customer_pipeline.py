"""Airflow orchestration for v0.3 audited Apache Hop ETL execution."""

from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timedelta
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

try:
    from airflow.sdk import DAG, get_current_context, task
except ImportError:  # Keep repository tests independent from an Airflow installation.
    DAG = None
    get_current_context = None
    task = None

DAG_ID = "hop_synthetic_customer_daily"
EXPECTED_RECORD_COUNT = 3
DEFAULT_PIPELINE_PATH = "${PROJECT_HOME}/pipelines/synthetic_customer_daily.hpl"
DEFAULT_AUDIT_START_PATH = "${PROJECT_HOME}/pipelines/audit_execution_start.hpl"
DEFAULT_AUDIT_FINALIZE_PATH = "${PROJECT_HOME}/pipelines/audit_execution_finalize.hpl"


def _decode_response(body: str):
    """Decode Hop JSON/XML responses into a small Python structure."""
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        try:
            root = ElementTree.fromstring(body)
        except ElementTree.ParseError:
            return {"raw": body}

        return {
            "result": root.findtext("result"),
            "message": root.findtext("message"),
            "id": root.findtext("id"),
        }


def _hop_request(path: str, query: dict[str, str] | None = None):
    base_url = os.getenv("HOP_BASE_URL", "http://hop:8181").rstrip("/")
    username = os.getenv("HOP_SERVER_USER", "hop-user")
    password = os.getenv("HOP_SERVER_PASS", "synthetic-hop-password")

    url = f"{base_url}{path}"
    if query:
        url = f"{url}?{urlencode(query)}"

    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    request = Request(
        url,
        headers={
            "Authorization": f"Basic {token}",
            "Accept": "application/json, application/xml;q=0.9",
        },
    )

    try:
        with urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            result = _decode_response(body)
            if isinstance(result, dict):
                result["http_status"] = response.status
            return result
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        result = _decode_response(body)
        if not isinstance(result, dict):
            result = {"raw": body}
        result["http_status"] = exc.code
        return result


def _execute_hop_pipeline(pipeline_path: str, parameters: dict[str, str]) -> dict:
    query = {
        "pipeline": pipeline_path,
        "runConfig": "local",
        "level": "Basic",
        "json": "Y",
        **parameters,
    }
    result = _hop_request("/hop/execPipeline", query)

    if str(result.get("result", "")).upper() != "OK":
        raise RuntimeError(f"Hop pipeline execution failed for {pipeline_path}: {result}")

    return result


def _runtime_identity() -> dict[str, str | int]:
    if get_current_context is None:
        raise RuntimeError("Airflow execution context is unavailable.")

    context = get_current_context()
    run_id = str(context["run_id"])
    attempt_number = int(context["ti"].try_number)
    environment_name = os.getenv("PLATFORM_ENV", "DEV").upper()
    trigger_type = run_id.split("__", 1)[0].upper() if "__" in run_id else "AIRFLOW"

    return {
        "run_id": run_id,
        "attempt_number": attempt_number,
        "environment_name": environment_name,
        "trigger_type": trigger_type,
        "correlation_id": f"{DAG_ID}:{run_id}",
    }


if DAG is not None:
    with DAG(
        dag_id=DAG_ID,
        description="Airflow -> Hop -> PostgreSQL with retry-aware ETL audit lifecycle",
        start_date=datetime(2026, 1, 1),
        schedule=None,
        catchup=False,
        tags=["synthetic", "airflow", "apache-hop", "postgresql", "audit", "v0.3"],
    ) as dag:

        @task
        def check_hop_server() -> dict:
            status = _hop_request("/hop/status/", {"json": "Y"})
            if not status or int(status.get("http_status", 200)) >= 400:
                raise RuntimeError(f"Hop Server health check failed: {status}")
            return {"hop_server": "reachable"}

        @task(retries=2, retry_delay=timedelta(seconds=10))
        def execute_etl_with_audit() -> dict:
            identity = _runtime_identity()

            common = {
                "RUN_ENV": str(identity["environment_name"]),
                "RUN_ID": str(identity["run_id"]),
                "ATTEMPT_NUMBER": str(identity["attempt_number"]),
                "CORRELATION_ID": str(identity["correlation_id"]),
            }

            audit_start_path = os.getenv(
                "HOP_AUDIT_START_PATH", DEFAULT_AUDIT_START_PATH
            )
            pipeline_path = os.getenv("HOP_PIPELINE_PATH", DEFAULT_PIPELINE_PATH)
            audit_finalize_path = os.getenv(
                "HOP_AUDIT_FINALIZE_PATH", DEFAULT_AUDIT_FINALIZE_PATH
            )

            _execute_hop_pipeline(
                audit_start_path,
                {
                    **common,
                    "TRIGGER_TYPE": str(identity["trigger_type"]),
                },
            )

            data_completed = False
            try:
                _execute_hop_pipeline(pipeline_path, common)
                data_completed = True

                _execute_hop_pipeline(
                    audit_finalize_path,
                    {
                        "RUN_ENV": str(identity["environment_name"]),
                        "RUN_ID": str(identity["run_id"]),
                        "ATTEMPT_NUMBER": str(identity["attempt_number"]),
                        "FINAL_STATUS": "SUCCESS",
                        "RECORDS_READ": str(EXPECTED_RECORD_COUNT),
                        "RECORDS_WRITTEN": str(EXPECTED_RECORD_COUNT),
                        "ERROR_MESSAGE": "",
                    },
                )
            except Exception as exc:
                failed_count = EXPECTED_RECORD_COUNT if data_completed else 0
                error_message = str(exc)[:1000]

                try:
                    _execute_hop_pipeline(
                        audit_finalize_path,
                        {
                            "RUN_ENV": str(identity["environment_name"]),
                            "RUN_ID": str(identity["run_id"]),
                            "ATTEMPT_NUMBER": str(identity["attempt_number"]),
                            "FINAL_STATUS": "FAILED",
                            "RECORDS_READ": str(failed_count),
                            "RECORDS_WRITTEN": str(failed_count),
                            "ERROR_MESSAGE": error_message,
                        },
                    )
                except Exception as audit_exc:
                    raise RuntimeError(
                        f"ETL failed and audit finalization also failed: {audit_exc}"
                    ) from exc

                raise

            return {
                "pipeline": pipeline_path,
                "environment": identity["environment_name"],
                "run_id": identity["run_id"],
                "attempt_number": identity["attempt_number"],
                "correlation_id": identity["correlation_id"],
                "records_written": EXPECTED_RECORD_COUNT,
                "result": "SUCCESS",
            }

        hop_health = check_hop_server()
        etl_execution = execute_etl_with_audit()
        hop_health >> etl_execution
