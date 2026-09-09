# Roadmap / 路線圖

## 繁體中文

### v0.1 — Foundation ✅
- Platform boundary / Docker Compose / CI / Security

### v0.2 — Executable Hop + Airflow Integration ✅
- Hop Server / executable pipeline / Airflow REST orchestration

### v0.3 — PostgreSQL Audit + Retry Lifecycle ✅
- retry-aware audit / lifecycle events / persisted target

### v0.4 — Immutable Supply Chain + Air-Gapped Bundle ✅
- packaged Hop runtime / same-image promotion / SBOM / signed offline bundle

### v0.5 — Prometheus/Grafana Observability + SLO/Alerting ✅

- read-only PostgreSQL observability views
- SQL Exporter 0.24.8
- Prometheus 3.14.0
- Alertmanager 0.34.0
- Grafana 13.2.1
- ETL execution/failure/retry metrics
- stale/last-success/duration metrics
- 99% success SLO
- error budget recording rules
- SLO/stale/no-recent-success alerts
- auto-provisioned operations dashboard
- executable observability CI smoke

### 後續版本

- v0.6：Deployment governance hardening、release/recovery scenarios

## English

### v0.1 — Foundation ✅
Platform boundaries and CI/security baseline.

### v0.2 — Executable Hop + Airflow Integration ✅
Real orchestration and executable Hop runtime.

### v0.3 — PostgreSQL Audit + Retry Lifecycle ✅
Retry-aware execution audit and persisted ETL output.

### v0.4 — Immutable Supply Chain + Air-Gapped Bundle ✅
Build-once promotion, image SBOM, signing, and offline delivery.

### v0.5 — Prometheus/Grafana Observability + SLO/Alerting ✅
Read-only metrics surface, SQL Exporter, Prometheus, Alertmanager, Grafana dashboard, a 99% SLO/error budget, operational alerts, and runtime CI proof.

### Future versions

- v0.6: deployment-governance hardening and failure-recovery scenarios
