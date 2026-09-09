# Enterprise ETL Platform

[繁體中文](#繁體中文) | [English](#english)

## 繁體中文

`enterprise-etl-platform` 是以 **Enterprise Data Engineering Platform** 為核心的作品集專案，涵蓋 ETL/ELT execution、Airflow orchestration、Apache Hop runtime、PostgreSQL audit、retry lifecycle、immutable supply chain、Air-Gapped deployment、Prometheus/Grafana observability、SLO 與 alerting。

### v0.5 — Executable Observability

v0.5 新增完整監控鏈：

```text
PostgreSQL Audit
      ↓
etl_observability read-only views
      ↓
SQL Exporter
      ↓
Prometheus
  ├─ ETL metrics
  ├─ SLO recording rules
  └─ alert rules
      ↓
Alertmanager
      ↓
Grafana
```

核心內容：

- SQL Exporter **0.24.8**
- Prometheus **3.14.0**
- Alertmanager **0.34.0**
- Grafana **13.2.1**
- read-only `etl_observability` schema
- least-privilege `etl_monitor` sample role
- ETL run / failure / retry counters
- records-written counter
- stale RUNNING gauge
- latest-success timestamp
- average / P95 duration
- **99% ETL success SLO**
- error ratio / error budget recording rules
- SLO breach / stale execution / no-recent-success alerts
- auto-provisioned Grafana datasource + dashboard
- runtime CI observability smoke

### Metrics

```text
etl_pipeline_run_total
etl_pipeline_failure_total
etl_pipeline_retry_total
etl_records_written_total
etl_running_stale_total
etl_last_success_timestamp_seconds
etl_pipeline_duration_seconds
etl_pipeline_duration_p95_seconds
```

### 快速驗證

```bash
cp .env.example .env
python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet

make lifecycle-smoke
make observability-smoke
make supply-chain-smoke
```

`make observability-smoke` 會實際建立 synthetic SUCCESS / FAILED / retry SUCCESS / stale RUNNING execution，然後驗證 Prometheus scrape、SLO rules、firing alerts、Alertmanager readiness、Grafana datasource 與 dashboard provisioning。

### 啟動 Monitoring Stack

```bash
docker compose --profile monitoring up -d
docker compose ps
```

- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`
- SQL Exporter: `http://localhost:9399/metrics`
- Dashboard: **Enterprise ETL Operations**

> Repository 只含 synthetic / generic configuration。正式 database、Grafana、Alertmanager credential 與 notification endpoint 應由部署環境注入。

詳細文件：

- `docs/OBSERVABILITY.md`
- `docs/SLO_ALERTING.md`
- `docs/AUDIT_LIFECYCLE.md`
- `docs/SUPPLY_CHAIN.md`
- `docs/GOVERNANCE.md`

## English

`enterprise-etl-platform` is an **Enterprise Data Engineering Platform** portfolio project covering ETL execution, orchestration, audit/retry lifecycle, immutable supply chain, air-gapped delivery, and executable observability.

v0.5 adds SQL Exporter 0.24.8, Prometheus 3.14.0, Alertmanager 0.34.0, Grafana 13.2.1, read-only ETL metric views, a 99% success SLO, error-budget recording rules, operational alerts, and an auto-provisioned operations dashboard.

`make observability-smoke` creates synthetic success/failure/retry/stale executions and proves metrics, SLO rules, firing alerts, Alertmanager, and Grafana provisioning at runtime.

All sample data, credentials, hostnames, schemas, and company information are synthetic or generic.
