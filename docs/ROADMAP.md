# Roadmap / 路線圖

## 繁體中文

### v0.1 — Foundation

- Platform boundary and architecture
- Docker Compose baseline
- Airflow DAG skeleton
- Hop workspace
- PostgreSQL audit schema
- DEV / TEST / PROD separation
- CI / Security / Trivy / SBOM
- Promotion, Air-Gapped, Observability documents

### 後續版本方向（不在 v0.1 實作）

- v0.2：可執行的 Hop pipeline + Airflow orchestration integration
- v0.3：完整 PostgreSQL audit logging、retry/error lifecycle、sample ETL
- v0.4：Image build/promotion、offline bundle、checksum/signing
- v0.5：Prometheus/Grafana observability、SLO/alert baseline
- v0.6：Deployment governance、release automation、failure recovery scenario

## English

### v0.1 — Foundation

The v0.1 scope establishes architecture, runtime skeletons, audit schema, environment separation, CI/security controls, and governance documentation.

### Future versions (not implemented in v0.1)

- v0.2: executable Hop pipeline and Airflow integration
- v0.3: complete audit logging, retry/error lifecycle, sample ETL
- v0.4: image build/promotion, offline bundle, checksum/signing
- v0.5: Prometheus/Grafana observability and SLO/alert baseline
- v0.6: deployment governance, release automation, failure-recovery scenario
