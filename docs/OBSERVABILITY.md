# Monitoring & Observability / 監控與可觀測性

## 繁體中文

v0.2 已有兩層可觀測資料來源，但完整 Prometheus/Grafana stack 仍保留給後續版本。

### Airflow layer

可觀察：

- DAG run status
- Task retry / failure
- Task duration
- Hop Server connectivity failure
- Hop execution response

DAG：`hop_synthetic_customer_daily`

### Hop layer

Hop Server / pipeline log 可觀察：

- pipeline start / finish
- transform execution
- `record_id`
- synthetic field output
- `RUN_ENV`
- execution error

```bash
docker compose logs -f hop
```

### PostgreSQL audit

`etl_audit.etl_execution_log` schema 已存在，但 v0.2 不假裝已完成 end-to-end database audit write。v0.3 將加入 execution id、status、records read/written、error lifecycle 與 retry correlation。

### Target metrics

- `etl_pipeline_run_total`
- `etl_pipeline_failure_total`
- `etl_pipeline_duration_seconds`
- `etl_records_read_total`
- `etl_records_written_total`
- `etl_last_success_timestamp`

## English

v0.2 exposes two observable layers: Airflow DAG/task state and Hop Server/pipeline logs. The PostgreSQL audit schema remains available, but complete end-to-end audit writes are intentionally not claimed until v0.3.

Future metrics include pipeline run/failure counts, duration, records read/written, and last-success timestamps.
