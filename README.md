# Enterprise ETL Platform

[繁體中文](#繁體中文) | [English](#english)

## 繁體中文

`enterprise-etl-platform` 是以 **Enterprise Data Engineering Platform** 為核心的作品集專案，主角是 ETL/ELT execution、Orchestration、Auditability、Retry lifecycle、環境分離、安全供應鏈、Container Image promotion、Air-Gapped deployment 與 Observability。

### 專案定位

| Repository | 核心角色 |
|---|---|
| `enterprise-rag-platform` | Knowledge AI Platform |
| `agentic-dataops-copilot` | AI Reasoning / DataOps Operations |
| `data-platform-mcp-server` | Tool / Integration Platform |
| `multi-llm-ai-gateway` | Model Control Plane |
| **`enterprise-etl-platform`** | **Data Engineering Platform** |

### v0.3 — Audited ETL Lifecycle

v0.3 的執行鏈：

```text
Airflow run_id / try_number
        ↓
audit_execution_start.hpl
        ↓
PostgreSQL RUNNING + STARTED event
        ↓
synthetic_customer_daily.hpl
        ↓
etl_data.synthetic_customer_daily
        ↓
audit_execution_finalize.hpl
        ↓
SUCCESS / FAILED + finished_at + lifecycle event
        ↓
Airflow retry when failed
```

核心內容：

- Apache Hop 2.19.0
- Apache Airflow 3.x style Task SDK DAG
- PostgreSQL execution audit
- `correlation_id` + `attempt_number`
- append-only lifecycle event
- retry-aware failure history
- persisted synthetic ETL target
- variable-driven Hop PostgreSQL connection
- DEV / TEST / PROD parameter separation
- executable PostgreSQL + Hop CI integration test
- Trivy / Secret Scan / CycloneDX SBOM
- gated Tag / Release

### 快速驗證

```bash
cp .env.example .env
python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
make lifecycle-smoke
```

`make lifecycle-smoke` 會實際驗證：

```text
attempt 1 → FAILED
attempt 2 → SUCCESS
lifecycle events → STARTED,FAILED,STARTED,SUCCEEDED
persisted target → 3 rows
```

### 啟動

```bash
docker compose --profile orchestration up -d
docker compose ps
```

- Airflow UI: `http://localhost:8080`
- Hop Server: `http://localhost:8181`
- PostgreSQL: `localhost:5432`
- DAG: `hop_synthetic_customer_daily`

> 所有 Sample Data、Hostname、Credential、Schema 與公司資訊均為 synthetic / generic。

詳細文件：

- `docs/ARCHITECTURE.md`
- `docs/ORCHESTRATION.md`
- `docs/AUDIT_LIFECYCLE.md`
- `docs/INSTALLATION.md`
- `docs/SECURITY.md`

## English

`enterprise-etl-platform` is an **Enterprise Data Engineering Platform** portfolio project focused on ETL/ELT execution, orchestration, auditability, retry lifecycle management, environment separation, supply-chain security, image promotion, air-gapped deployment, and observability.

### v0.3 — Audited ETL Lifecycle

v0.3 correlates Airflow `run_id` and `try_number` with Apache Hop execution, PostgreSQL lifecycle audit, and persisted synthetic target rows.

It introduces retry-aware execution attempts, append-only STARTED/SUCCEEDED/FAILED events, persisted ETL output, variable-driven PostgreSQL connection metadata, and a real CI integration test that proves a failed first attempt and successful retry remain separately auditable.

### Quick validation

```bash
cp .env.example .env
python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
make lifecycle-smoke
```

All sample data, hostnames, credentials, schemas, and company information are synthetic or generic.
