"""Synthetic Airflow DAG used only for portfolio validation."""

from datetime import datetime

try:
    from airflow.sdk import DAG, task
except ImportError:
    DAG = None
    task = None

DAG_ID = "synthetic_customer_daily"

if DAG is not None:
    with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1),
        schedule=None,
        catchup=False,
        tags=["synthetic", "portfolio", "v0.1"],
    ) as dag:

        @task
        def extract() -> list[dict]:
            return [
                {"customer_id": "CUST-0001", "amount": 120.0},
                {"customer_id": "CUST-0002", "amount": 80.0},
            ]

        @task
        def transform(rows: list[dict]) -> dict:
            return {
                "record_count": len(rows),
                "total_amount": sum(row["amount"] for row in rows),
            }

        transform(extract())
