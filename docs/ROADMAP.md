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
- read-only observability views / metrics / alerting / dashboard / runtime smoke

### v0.6 — ETL Intelligence + Enterprise Delivery Security ✅
- deterministic ETL parser
- normalized metadata / evidence / provenance
- AI semantic boundary / structured output / fallback / sensitive filtering
- GitLab CI/CD enterprise reference
- TEST → PROD same-registry-digest promotion
- CVE applicability / remediation lifecycle
- SBOM diff / CVE gate / digest verification / regression evidence
- deployment governance / rollback identity rules

### 後續版本

v0.7 僅在作品集確有新增價值時再考慮 multi-environment recovery drill、HA/DR exercise 或更完整 parser adapters；不為版本號而新增功能。

## English

v0.1 through v0.5 establish the executable data-engineering runtime, audit, immutable delivery, air-gapped packaging, and observability layers.

### v0.6 — ETL Intelligence + Enterprise Delivery Security ✅

v0.6 adds deterministic design-time ETL parsing, normalized provenance/evidence, an evidence-bound AI semantic layer with fallback, an executable GitLab delivery reference, same-digest environment promotion, and a remediation-driven vulnerability lifecycle.

Future work is optional and must add portfolio value rather than duplicate adjacent repositories.
