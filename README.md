# Enterprise ETL Platform

[繁體中文](#繁體中文) | [English](#english)

## 繁體中文

`enterprise-etl-platform` 是以 **Data Engineering Platform** 為核心的作品集專案，聚焦 ETL/ELT 執行、排程、稽核、環境分離、安全供應鏈、Container Image promotion、Air-Gapped deployment 與 Observability。

### 專案定位

本專案刻意與其他平台型作品區隔：

| Repository | 核心角色 |
|---|---|
| `enterprise-rag-platform` | Knowledge AI Platform |
| `agentic-dataops-copilot` | AI Reasoning / DataOps Operations |
| `data-platform-mcp-server` | Tool / Integration Platform |
| `multi-llm-ai-gateway` | Model Control Plane |
| **`enterprise-etl-platform`** | **Data Engineering Platform** |

### v0.1 Foundation

- Apache Airflow orchestration skeleton
- Apache Hop project workspace
- PostgreSQL Audit / ETL Execution Log schema
- Docker Compose local platform baseline
- DEV / TEST / PROD configuration separation
- GitLab-style promotion and deployment governance
- GitHub Actions CI / Security verification
- Trivy filesystem security scan
- SBOM generation
- Repository-level secret scanning
- Offline / Air-Gapped deployment design
- Monitoring / Observability baseline

### 快速開始

```bash
cp .env.example .env
python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
docker compose up -d postgres
```

> v0.1 不將真實 Credential 寫入 Repository。所有 Sample Data、Hostname、Schema 與設定皆為 synthetic / generic。

詳細文件：`docs/`

## English

`enterprise-etl-platform` is a portfolio project centered on an **Enterprise Data Engineering Platform**. It focuses on ETL/ELT execution, orchestration, auditability, environment separation, software supply-chain security, container image promotion, air-gapped deployment, and observability.

### Positioning

This repository is intentionally separated from the other platform projects:

| Repository | Primary role |
|---|---|
| `enterprise-rag-platform` | Knowledge AI Platform |
| `agentic-dataops-copilot` | AI Reasoning / DataOps Operations |
| `data-platform-mcp-server` | Tool / Integration Platform |
| `multi-llm-ai-gateway` | Model Control Plane |
| **`enterprise-etl-platform`** | **Data Engineering Platform** |

### v0.1 Foundation

- Apache Airflow orchestration skeleton
- Apache Hop project workspace
- PostgreSQL Audit / ETL Execution Log schema
- Docker Compose local platform baseline
- DEV / TEST / PROD configuration separation
- GitLab-style promotion and deployment governance
- GitHub Actions CI / Security verification
- Trivy filesystem security scan
- SBOM generation
- Repository-level secret scanning
- Offline / Air-Gapped deployment design
- Monitoring / Observability baseline

### Quick start

```bash
cp .env.example .env
python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
docker compose up -d postgres
```

> v0.1 stores no real credentials in the repository. All sample data, hostnames, schemas, and settings are synthetic or generic.

See `docs/` for detailed documentation.
