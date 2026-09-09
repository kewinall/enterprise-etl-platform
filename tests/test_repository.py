import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryBaselineTest(unittest.TestCase):
    def test_version_is_v0_1(self):
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.1.0")

    def test_audit_schema_exists(self):
        sql = (ROOT / "postgres/init/001_etl_audit.sql").read_text()
        self.assertIn("etl_execution_log", sql)
        self.assertIn("pipeline_name", sql)

    def test_sample_airflow_dag_is_synthetic(self):
        dag = (ROOT / "airflow/dags/sample_etl_pipeline.py").read_text()
        self.assertIn("synthetic_customer_daily", dag)
        self.assertNotIn("real-customer", dag)


if __name__ == "__main__":
    unittest.main()
