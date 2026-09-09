# Troubleshooting / 疑難排解

## 繁體中文

### `make observability-smoke` 失敗

先確認：

```bash
docker version
docker pull postgres:16-alpine
docker pull burningalchemist/sql_exporter:0.24.8
docker pull prom/prometheus:v3.14.0
docker pull prom/alertmanager:v0.34.0
docker pull grafana/grafana:13.2.1
```

### SQL Exporter 無 metrics

檢查：

```bash
curl http://localhost:9399/metrics
docker compose logs sql-exporter
```

並確認 `003_v0_5_observability.sql` 已套用。

### Prometheus target down

Prometheus UI：

`Status → Targets`

或：

```bash
curl http://localhost:9090/api/v1/targets
```

確認 `sql-exporter:9399` 可由 Prometheus container network 存取。

### Prometheus rule 無法載入

```bash
docker run --rm \
  --entrypoint /bin/promtool \
  -v "$PWD/monitoring/prometheus:/etc/prometheus:ro" \
  prom/prometheus:v3.14.0 \
  check config /etc/prometheus/prometheus.yml
```

### SLO alert 沒有 firing

先確認 final status counters：

```promql
etl_pipeline_run_total
```

再確認 recording rule：

```promql
etl:slo_success_ratio
```

若只有 RUNNING row，success ratio 不會產生；SLO 只計 final SUCCESS/FAILED。

### Stale alert 沒有 firing

確認：

```promql
etl_running_stale_total
```

Stale threshold 是 RUNNING 超過 30 分鐘。

### Grafana dashboard 不存在

```bash
docker compose logs grafana
```

確認：

- provisioning datasource path
- dashboard provider path
- `enterprise-etl-operations.json`

### Grafana datasource error

確認 container DNS 可解析：

`prometheus:9090`

不要把 datasource URL 改成 Grafana container 內的 `localhost:9090`。

### 既有 v0.4 database 找不到 observability views

套用：

`postgres/init/003_v0_5_observability.sql`

PostgreSQL 不會對既有 volume 自動重跑 init scripts。

### Supply-chain / lifecycle failure

v0.3 lifecycle 與 v0.4 supply-chain troubleshooting 原則仍適用；v0.5 CI 仍會跑這兩層 smoke test。

## English

If the observability smoke fails, verify the pinned PostgreSQL, SQL Exporter, Prometheus, Alertmanager, and Grafana images are available.

Missing metrics usually indicate the v0.5 observability migration was not applied or SQL Exporter cannot read the views. Prometheus target/rule APIs should be checked before debugging Grafana.

SLO calculations use only final SUCCESS/FAILED attempts. Stale RUNNING executions are a separate gauge and alert.

For an existing v0.4 volume, apply the v0.5 migration manually.
