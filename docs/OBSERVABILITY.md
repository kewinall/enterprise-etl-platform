# Monitoring & Observability / 監控與可觀測性

## 繁體中文

v0.3 已有三層可觀測來源：

1. Airflow DAG / task state
2. Hop Server execution log
3. PostgreSQL structured execution audit

### PostgreSQL operational views

失敗 execution：

```sql
SELECT
    pipeline_name,
    environment_name,
    run_id,
    attempt_number,
    error_message,
    started_at,
    finished_at
FROM etl_audit.etl_execution_log
WHERE status = 'FAILED'
ORDER BY started_at DESC;
```

Retry 次數：

```sql
SELECT
    correlation_id,
    count(*) AS attempts,
    max(attempt_number) AS max_attempt
FROM etl_audit.etl_execution_log
GROUP BY correlation_id
HAVING count(*) > 1;
```

Incomplete execution：

```sql
SELECT *
FROM etl_audit.etl_execution_log
WHERE status = 'RUNNING'
  AND started_at < CURRENT_TIMESTAMP - INTERVAL '30 minutes';
```

Lifecycle：

```sql
SELECT
    l.run_id,
    l.attempt_number,
    e.event_type,
    e.event_at,
    e.message
FROM etl_audit.etl_execution_log l
JOIN etl_audit.etl_execution_event e
  ON e.execution_id = l.execution_id
ORDER BY e.event_at DESC;
```

### Target traceability

`etl_data.synthetic_customer_daily` 可用 `run_id + attempt_number` join 回 audit table。

### Target metrics

- `etl_pipeline_run_total`
- `etl_pipeline_failure_total`
- `etl_pipeline_retry_total`
- `etl_pipeline_duration_seconds`
- `etl_records_written_total`
- `etl_running_stale_total`
- `etl_last_success_timestamp`

v0.5 才會把這些正式暴露到 Prometheus/Grafana 與 alert/SLO。

## English

v0.3 provides three observable layers: Airflow task state, Hop Server execution logs, and structured PostgreSQL audit data.

The audit tables now support direct queries for failed attempts, retry counts, stale RUNNING executions, lifecycle events, and target-data traceability.

Prometheus/Grafana metric export, alert rules, and SLOs remain v0.5 scope.
