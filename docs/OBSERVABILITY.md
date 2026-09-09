# Monitoring & Observability / 監控與可觀測性

## 繁體中文

v0.1 先定義觀測模型，不在此版本建置完整 Prometheus/Grafana stack。

### 三個觀測面向

- **Execution**：pipeline status、duration、retry、records read/written。
- **Platform**：Airflow scheduler/worker、Hop runtime、PostgreSQL health/resource。
- **Governance**：deployment version、image digest、environment、release、audit trail。

### 建議 Metrics

- `etl_pipeline_run_total`
- `etl_pipeline_failure_total`
- `etl_pipeline_duration_seconds`
- `etl_records_read_total`
- `etl_records_written_total`
- `etl_last_success_timestamp`

PostgreSQL 的 `etl_audit.etl_execution_log` 是 v0.1 operational audit 的基礎資料來源。

## English

v0.1 defines the observability model without deploying a full Prometheus/Grafana stack yet.

The model covers execution metrics, platform health, and governance metadata. Recommended metrics include pipeline run/failure counts, duration, records read/written, and last-success timestamps. The PostgreSQL `etl_audit.etl_execution_log` table is the initial operational audit source.
