import json
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


class RepositoryBaselineTest(unittest.TestCase):
    def test_version_is_v0_6(self):
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.6.0")

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

    def test_compose_uses_packaged_hop_runtime(self):
        compose = (ROOT / "docker-compose.yml").read_text()
        self.assertIn("enterprise-etl-hop:local", compose)
        self.assertIn("docker/hop-runtime.Dockerfile", compose)
        self.assertIn("HOP_PROJECT_FOLDER: /opt/enterprise-etl/project", compose)
        self.assertIn("HOP_ENVIRONMENT_NAME: compose", compose)
        self.assertIn("./hop/environments/compose.json", compose)
        self.assertNotIn("./hop/projects/enterprise-etl:/files/project", compose)

        environment = json.loads((ROOT / "hop/environments/compose.json").read_text())
        variables = {item["name"]: item["value"] for item in environment["variables"]}
        self.assertEqual(variables["POSTGRES_HOST"], "postgres")
        self.assertEqual(variables["POSTGRES_PORT"], "5432")

    def test_runtime_dockerfile_bakes_project_and_provenance_labels(self):
        dockerfile = (ROOT / "docker/hop-runtime.Dockerfile").read_text()
        self.assertIn("FROM apache/hop:2.19.0", dockerfile)
        self.assertIn("COPY --chown=hop:hop hop/projects/enterprise-etl", dockerfile)
        self.assertIn("org.opencontainers.image.version", dockerfile)
        self.assertIn("org.opencontainers.image.revision", dockerfile)
        self.assertIn("/opt/enterprise-etl/project", dockerfile)

    def test_promotion_script_enforces_same_image_id(self):
        script = (ROOT / "scripts/promote_image.sh").read_text()
        self.assertIn("docker tag", script)
        self.assertIn("docker image inspect", script)
        self.assertIn("SOURCE_ID", script)
        self.assertIn("TARGET_ID", script)
        self.assertIn('SOURCE_ID}" != "${TARGET_ID}', script)

    def test_offline_bundle_contains_sbom_checksum_and_signature(self):
        script = (ROOT / "scripts/create_offline_bundle.sh").read_text()
        for token in (
            "anchore/syft:v1.51.1",
            "cyclonedx-json",
            "docker save",
            "SHA256SUMS",
            "sha256sum",
            "openssl dgst -sha256 -sign",
            "manifest.json",
            "promotion_policy",
        ):
            self.assertIn(token, script)

    def test_offline_verifier_loads_and_checks_image_identity(self):
        script = (ROOT / "scripts/verify_offline_bundle.sh").read_text()
        for token in (
            "openssl dgst -sha256 -verify",
            "sha256sum -c",
            "docker load",
            "EXPECTED_IMAGE_ID",
            "LOADED_IMAGE_ID",
        ):
            self.assertIn(token, script)

    def test_lifecycle_smoke_validates_retry_and_persistence(self):
        smoke = (ROOT / "scripts/etl_lifecycle_smoke.sh").read_text()
        self.assertIn("HOP_ENVIRONMENT_CONFIG_FILE_NAME_PATHS", smoke)
        self.assertIn("1:FAILED:0:synthetic retry validation", smoke)
        self.assertIn("2:SUCCESS:3:", smoke)
        self.assertIn("STARTED,FAILED,STARTED,SUCCEEDED", smoke)
        self.assertIn('target_count}" != "3"', smoke)

    def test_supply_chain_smoke_proves_build_once_promotion_and_reload(self):
        smoke = (ROOT / "scripts/supply_chain_smoke.sh").read_text()
        for token in (
            "candidate-v",
            "test-v",
            "prod-v",
            "promote_image.sh",
            "create_offline_bundle.sh",
            "verify_offline_bundle.sh",
            "EXPECTED_IMAGE_ID",
            "LOADED_ID",
        ):
            self.assertIn(token, smoke)

    def test_ci_uploads_validated_offline_bundle(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("supply_chain_smoke.sh", ci)
        self.assertIn("actions/upload-artifact@v4", ci)
        self.assertIn("name: offline-bundle", ci)

    def test_release_attaches_ci_offline_assets(self):
        release = (ROOT / ".github/workflows/release.yml").read_text()
        self.assertIn("gh run download", release)
        self.assertIn("--name offline-bundle", release)
        self.assertIn("gh release upload", release)
        self.assertIn("--clobber", release)


    def test_v0_5_observability_schema_is_read_only_surface(self):
        sql = (ROOT / "postgres/init/003_v0_5_observability.sql").read_text()
        for token in (
            "etl_observability",
            "pipeline_status_totals",
            "pipeline_runtime_metrics",
            "etl_monitor",
            "synthetic-monitor-password",
            "stale_running",
            "p95_duration_seconds",
        ):
            self.assertIn(token, sql)
        self.assertIn("WHERE status IN ('SUCCESS', 'FAILED')", sql)

    def test_sql_exporter_exposes_etl_metric_contract(self):
        collector = (
            ROOT / "monitoring/sql-exporter/etl_audit.collector.yml"
        ).read_text()
        for metric in (
            "etl_pipeline_run_total",
            "etl_pipeline_failure_total",
            "etl_pipeline_retry_total",
            "etl_records_written_total",
            "etl_running_stale_total",
            "etl_last_success_timestamp_seconds",
            "etl_pipeline_duration_seconds",
            "etl_pipeline_duration_p95_seconds",
        ):
            self.assertIn(metric, collector)

        config = (ROOT / "monitoring/sql-exporter/sql_exporter.yml").read_text()
        self.assertIn("etl_monitor", config)
        self.assertIn("etl_audit", config)

    def test_prometheus_has_slo_recording_and_alert_rules(self):
        config = (ROOT / "monitoring/prometheus/prometheus.yml").read_text()
        rules = (ROOT / "monitoring/prometheus/rules/etl.rules.yml").read_text()
        self.assertIn("sql-exporter:9399", config)
        self.assertIn("alertmanager:9093", config)
        for token in (
            "etl:slo_success_ratio",
            "etl:slo_error_ratio",
            "etl:slo_error_budget_remaining",
            "ETLPipelineSLOBreach",
            "ETLStaleRunningExecution",
            "ETLNoRecentSuccess",
            "0.99",
        ):
            self.assertIn(token, rules)

    def test_grafana_dashboard_and_datasource_are_provisioned(self):
        dashboard = json.loads(
            (
                ROOT
                / "monitoring/grafana/dashboards/enterprise-etl-operations.json"
            ).read_text()
        )
        self.assertEqual(dashboard["uid"], "enterprise-etl-ops")
        self.assertEqual(dashboard["title"], "Enterprise ETL Operations")
        self.assertGreaterEqual(len(dashboard["panels"]), 8)

        datasource = (
            ROOT
            / "monitoring/grafana/provisioning/datasources/prometheus.yml"
        ).read_text()
        self.assertIn("uid: prometheus", datasource)
        self.assertIn("http://prometheus:9090", datasource)

    def test_compose_has_monitoring_profile(self):
        compose = (ROOT / "docker-compose.yml").read_text()
        for token in (
            "burningalchemist/sql_exporter:0.24.8",
            "prom/prometheus:v3.14.0",
            "prom/alertmanager:v0.34.0",
            "grafana/grafana:13.2.1",
            'profiles: ["monitoring"]',
            "./monitoring/prometheus",
            "./monitoring/grafana",
        ):
            self.assertIn(token, compose)

    def test_observability_smoke_proves_metrics_rules_alerts_and_dashboard(self):
        smoke = (ROOT / "scripts/observability_smoke.sh").read_text()
        for token in (
            "promtool",
            "etl_pipeline_run_total",
            "etl_pipeline_failure_total",
            "ETLPipelineSLOBreach",
            "ETLStaleRunningExecution",
            "/api/v1/alerts",
            "/api/search",
            "enterprise-etl-ops",
        ):
            self.assertIn(token, smoke)

    def test_ci_runs_observability_smoke(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("observability_smoke.sh", ci)


    def test_observability_waits_for_target_database_query(self):
        smoke = (ROOT / "scripts/observability_smoke.sh").read_text()
        self.assertIn("psql -U", smoke)
        self.assertIn("-Atqc 'SELECT 1'", smoke)
        self.assertIn("PostgreSQL target database did not become ready", smoke)



if __name__ == "__main__":
    unittest.main()
