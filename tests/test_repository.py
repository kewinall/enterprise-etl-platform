import json
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


class RepositoryBaselineTest(unittest.TestCase):
    def test_version_is_v0_2(self):
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.2.0")

    def test_audit_schema_exists(self):
        sql = (ROOT / "postgres/init/001_etl_audit.sql").read_text()
        self.assertIn("etl_execution_log", sql)
        self.assertIn("pipeline_name", sql)

    def test_hop_project_configuration_exists(self):
        project_config = ROOT / "hop/projects/enterprise-etl/project-config.json"
        self.assertTrue(project_config.exists())
        self.assertIn("metadataBaseFolder", project_config.read_text())

    def test_hop_local_run_configuration_exists(self):
        run_config = (
            ROOT
            / "hop/projects/enterprise-etl/metadata/pipeline-run-configuration/local.json"
        )
        payload = json.loads(run_config.read_text())
        self.assertEqual(payload["name"], "local")
        self.assertIn("Local", payload["engineRunConfiguration"])

    def test_hop_pipeline_is_executable_structure(self):
        pipeline = ROOT / "hop/projects/enterprise-etl/pipelines/synthetic_customer_daily.hpl"
        tree = ElementTree.parse(pipeline)
        root = tree.getroot()

        self.assertEqual(root.tag, "pipeline")
        self.assertEqual(root.findtext("./info/name"), "synthetic_customer_daily")

        transform_types = {
            transform.findtext("type")
            for transform in root.findall("./transform")
        }
        self.assertTrue({"RowGenerator", "Sequence", "WriteToLog"} <= transform_types)

        parameters = {
            parameter.findtext("name")
            for parameter in root.findall("./info/parameters/parameter")
        }
        self.assertIn("RUN_ENV", parameters)

    def test_airflow_dag_calls_hop_server(self):
        dag = (
            ROOT / "airflow/dags/hop_synthetic_customer_pipeline.py"
        ).read_text()
        self.assertIn('DAG_ID = "hop_synthetic_customer_daily"', dag)
        self.assertIn("/hop/execPipeline", dag)
        self.assertIn("HOP_PIPELINE_PATH", dag)
        self.assertIn("RUN_ENV", dag)

    def test_compose_pins_hop_2_19_and_exposes_orchestration(self):
        compose = (ROOT / "docker-compose.yml").read_text()
        self.assertIn("apache/hop:2.19.0", compose)
        self.assertIn('profiles: ["etl", "orchestration"]', compose)
        self.assertIn("command: standalone", compose)


if __name__ == "__main__":
    unittest.main()
