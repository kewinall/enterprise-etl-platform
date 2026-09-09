# Monitoring & Observability / 監控與可觀測性

## 繁體中文

### Monitoring stack

v0.5 正式實作：

```text
PostgreSQL
  ↓
etl_observability views
  ↓
SQL Exporter :9399
  ↓
Prometheus :9090
  ├─ recording rules
  └─ alert rules
      ↓
Alertmanager :9093

Prometheus
  ↓
Grafana :3000
```

Pinned versions：

| Component | Version |
|---|---|
| SQL Exporter | 0.24.8 |
| Prometheus | 3.14.0 |
| Alertmanager | 0.34.0 |
| Grafana | 13.2.1 |

### Metric contract

| Metric | Type | Meaning |
|---|---|---|
| `etl_pipeline_run_total` | counter | completed attempts by final status |
| `etl_pipeline_failure_total` | counter | failed attempts |
| `etl_pipeline_retry_total` | counter | retry attempts |
| `etl_records_written_total` | counter | audited written records |
| `etl_running_stale_total` | gauge | RUNNING > 30m |
| `etl_last_success_timestamp_seconds` | gauge | latest success epoch |
| `etl_pipeline_duration_seconds` | gauge | average completed duration |
| `etl_pipeline_duration_p95_seconds` | gauge | P95 completed duration |

### Why counters exclude RUNNING

Execution row 會從 `RUNNING` 更新成 `SUCCESS` / `FAILED`。若將 RUNNING count 當 counter，狀態轉換會造成值下降，違反 Prometheus counter semantics。

因此：

- final attempts → counter
- stale/current state → gauge

### Grafana dashboard

Provisioned dashboard：

**Enterprise ETL Operations**

包含：

- SLO Success Ratio
- Error Budget Remaining
- Stale RUNNING
- Retry Attempts
- Execution Attempts by Status
- Average / P95 Duration
- Records Written
- Last Success Age

Datasource provisioning：

`monitoring/grafana/provisioning/datasources/prometheus.yml`

### Local start

```bash
docker compose --profile monitoring up -d
```

### Runtime verification

```bash
make observability-smoke
```

Smoke test 驗證：

- PostgreSQL observability migration
- SQL Exporter metrics
- Prometheus config/rules
- Prometheus query API
- firing SLO/stale alerts
- Alertmanager readiness
- Grafana datasource
- Grafana dashboard

## English

v0.5 implements the monitoring stack rather than merely documenting target metrics.

A read-only PostgreSQL observability surface feeds SQL Exporter, which Prometheus scrapes. Prometheus evaluates recording and alert rules, Alertmanager provides the routing baseline, and Grafana is provisioned with an operations dashboard.

Final execution attempts are counters; current/stale state is exposed as gauges to preserve Prometheus metric semantics.

The executable observability smoke test validates the complete runtime path.
