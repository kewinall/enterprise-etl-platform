import json
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


class RepositoryBaselineTest(unittest.TestCase):
    def test_version_is_v0_3(self):
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.3.0")

    def test_v0_3_audit_schema_models_retry_lifecycle(self):
        sql = (ROOT / "postgres/init/002_v0_3_audit_lifecycle.sql").read_text()
        for token in (
            "correlation_id",
            "attempt_number",
            "trigger_type",
            "etl_execution_event",
            "STARTED",
            "SUCCEEDED",
            "FAILED",
            "synthetic_customer_daily",
        ):
            self.assertIn(token, sql)

    def test_hop_postgres_connection_is_variable_driven(self):
        connection_file = (
            ROOT
            / "hop/projects/enterprise-etl/metadata/rdbms/audit-postgres.json"
        )
        payload = json.loads(connection_file.read_text())
        postgres = payload["rdbms"]["POSTGRESQL"]

        self.assertEqual(payload["name"], "audit-postgres")
        self.assertEqual(postgres["hostname"], "${POSTGRES_HOST}")
        self.assertEqual(postgres["databaseName"], "${POSTGRES_DB}")
        self.assertEqual(postgres["username"], "${POSTGRES_USER}")
        self.assertEqual(postgres["password"], "${POSTGRES_PASSWORD}")

    def test_hop_local_run_configuration_exists(self):
        run_config = (
            ROOT
            / "hop/projects/enterprise-etl/metadata/pipeline-run-configuration/local.json"
        )
        payload = json.loads(run_config.read_text())
        self.assertEqual(payload["name"], "local")
        self.assertIn("Local", payload["engineRunConfiguration"])

    def test_data_pipeline_persists_run_correlated_rows(self):
        pipeline = (
            ROOT
            / "hop/projects/enterprise-etl/pipelines/synthetic_customer_daily.hpl"
        )
        root = ElementTree.parse(pipeline).getroot()

        self.assertEqual(root.findtext("./info/name"), "synthetic_customer_daily")
        transform_types = {
            transform.findtext("type") for transform in root.findall("./transform")
        }
        self.assertTrue(
            {"RowGenerator", "GetVariable", "Sequence", "TableOutput"}
            <= transform_types
        )

        parameters = {
            parameter.findtext("name")
            for parameter in root.findall("./info/parameters/parameter")
        }
        self.assertTrue(
            {"RUN_ENV", "RUN_ID", "ATTEMPT_NUMBER", "CORRELATION_ID"} <= parameters
        )

        table_output = next(
            transform
            for transform in root.findall("./transform")
            if transform.findtext("type") == "TableOutput"
        )
        self.assertEqual(table_output.findtext("connection"), "audit-postgres")
        self.assertEqual(table_output.findtext("schema"), "etl_data")
        self.assertEqual(table_output.findtext("table"), "synthetic_customer_daily")

    def test_audit_start_pipeline_inserts_running_attempt(self):
        pipeline = (
            ROOT
            / "hop/projects/enterprise-etl/pipelines/audit_execution_start.hpl"
        )
        root = ElementTree.parse(pipeline).getroot()
        self.assertEqual(root.findtext("./info/name"), "audit_execution_start")
        transform_types = {
            transform.findtext("type") for transform in root.findall("./transform")
        }
        self.assertIn("GetVariable", transform_types)
        self.assertIn("TableOutput", transform_types)
        self.assertIn("RUNNING", pipeline.read_text())

    def test_audit_finalize_pipeline_updates_attempt(self):
        pipeline = (
            ROOT
            / "hop/projects/enterprise-etl/pipelines/audit_execution_finalize.hpl"
        )
        root = ElementTree.parse(pipeline).getroot()
        self.assertEqual(root.findtext("./info/name"), "audit_execution_finalize")
        transform_types = {
            transform.findtext("type") for transform in root.findall("./transform")
        }
        self.assertIn("GetVariable", transform_types)
        self.assertIn("Update", transform_types)
        text = pipeline.read_text()
        self.assertIn("FINAL_STATUS", text)
        self.assertIn("ERROR_MESSAGE", text)
        self.assertIn("records_written", text)

    def test_airflow_dag_is_retry_and_audit_aware(self):
        dag = (
            ROOT / "airflow/dags/hop_synthetic_customer_pipeline.py"
        ).read_text()
        for token in (
            "get_current_context",
            'context["ti"].try_number',
            "HOP_AUDIT_START_PATH",
            "HOP_AUDIT_FINALIZE_PATH",
            '"FINAL_STATUS": "SUCCESS"',
            '"FINAL_STATUS": "FAILED"',
            "correlation_id",
        ):
            self.assertIn(token, dag)

    def test_compose_registers_hop_environment_for_postgres(self):
        compose = (ROOT / "docker-compose.yml").read_text()
        self.assertIn("apache/hop:2.19.0", compose)
        self.assertIn("HOP_ENVIRONMENT_NAME: compose", compose)
        self.assertIn(
            "HOP_ENVIRONMENT_CONFIG_FILE_NAME_PATHS: /files/environment/compose.json",
            compose,
        )
        self.assertIn("./hop/environments/compose.json", compose)
        self.assertIn("HOP_AUDIT_START_PATH", compose)
        self.assertIn("HOP_AUDIT_FINALIZE_PATH", compose)

        environment = json.loads((ROOT / "hop/environments/compose.json").read_text())
        variables = {item["name"]: item["value"] for item in environment["variables"]}
        self.assertEqual(variables["POSTGRES_HOST"], "postgres")
        self.assertEqual(variables["POSTGRES_PORT"], "5432")

    def test_lifecycle_smoke_validates_retry_and_persistence(self):
        smoke = (ROOT / "scripts/etl_lifecycle_smoke.sh").read_text()
        self.assertIn("HOP_ENVIRONMENT_CONFIG_FILE_NAME_PATHS", smoke)
        self.assertIn("1:FAILED:0:synthetic retry validation", smoke)
        self.assertIn("2:SUCCESS:3:", smoke)
        self.assertIn("STARTED,FAILED,STARTED,SUCCEEDED", smoke)
        self.assertIn('target_count}" != "3"', smoke)


if __name__ == "__main__":
    unittest.main()
