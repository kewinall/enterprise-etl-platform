"""Airflow orchestration for the v0.2 Apache Hop synthetic pipeline."""

from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

try:
    from airflow.sdk import DAG, task
except ImportError:  # Keep repository tests independent from an Airflow installation.
    DAG = None
    task = None

DAG_ID = "hop_synthetic_customer_daily"
DEFAULT_PIPELINE_PATH = "${PROJECT_HOME}/pipelines/synthetic_customer_daily.hpl"


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

    with urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")

    return _decode_response(body)


if DAG is not None:
    with DAG(
        dag_id=DAG_ID,
        description="Airflow -> Hop Server -> executable Apache Hop pipeline",
        start_date=datetime(2026, 1, 1),
        schedule=None,
        catchup=False,
        tags=["synthetic", "airflow", "apache-hop", "v0.2"],
        default_args={
            "retries": 2,
            "retry_delay": timedelta(seconds=10),
        },
    ) as dag:

        @task
        def check_hop_server() -> dict:
            status = _hop_request("/hop/status/", {"json": "Y"})
            if not status:
                raise RuntimeError("Hop Server returned an empty status response.")
            return {"hop_server": "reachable"}

        @task
        def execute_hop_pipeline() -> dict:
            pipeline_path = os.getenv("HOP_PIPELINE_PATH", DEFAULT_PIPELINE_PATH)
            environment_name = os.getenv("PLATFORM_ENV", "DEV").upper()

            result = _hop_request(
                "/hop/execPipeline",
                {
                    "pipeline": pipeline_path,
                    "runConfig": "local",
                    "level": "Basic",
                    "json": "Y",
                    "RUN_ENV": environment_name,
                },
            )

            if str(result.get("result", "")).upper() != "OK":
                raise RuntimeError(f"Hop pipeline execution failed: {result}")

            return {
                "pipeline": pipeline_path,
                "environment": environment_name,
                "result": "OK",
            }

        hop_health = check_hop_server()
        hop_execution = execute_hop_pipeline()
        hop_health >> hop_execution
