# Enterprise ETL Platform

[繁體中文](#繁體中文) | [English](#english)

## 繁體中文

`enterprise-etl-platform` 是以 **Enterprise Data Engineering Platform** 為核心的作品集專案，涵蓋 ETL/ELT execution、Airflow orchestration、Apache Hop runtime、PostgreSQL audit、retry lifecycle、software supply chain、Air-Gapped deployment 與 Observability。

### 專案定位

| Repository | 核心角色 |
|---|---|
| `enterprise-rag-platform` | Knowledge AI Platform |
| `agentic-dataops-copilot` | AI Reasoning / DataOps Operations |
| `data-platform-mcp-server` | Tool / Integration Platform |
| `multi-llm-ai-gateway` | Model Control Plane |
| **`enterprise-etl-platform`** | **Data Engineering Platform** |

### v0.4 — Immutable Supply Chain

v0.4 在 v0.3 的 audited ETL lifecycle 上加入：

- Immutable Apache Hop runtime image
- ETL project bake into image
- OCI version / revision / source labels
- Build once → TEST → PROD promotion
- Same `sha256` image ID enforcement
- Syft CycloneDX image SBOM
- Docker offline image archive
- Promotion manifest
- SHA-256 checksums
- OpenSSL detached signatures
- Air-Gapped verification / `docker load`
- GitHub Release offline bundle assets

Supply-chain flow：

```text
Source Commit
     ↓
Build Candidate Image
     ↓
Immutable Image ID
     ↓
TEST reference
     ↓
Approval
     ↓
PROD reference
     ↓
Offline Bundle
     ├─ image archive
     ├─ CycloneDX SBOM
     ├─ manifest
     ├─ SHA256SUMS
     └─ detached signature
```

**PROD 不重新 build。**

### ETL lifecycle

v0.3 的 execution/audit 能力完整保留：

```text
Airflow run_id / try_number
        ↓
audit_execution_start.hpl
        ↓
PostgreSQL RUNNING + STARTED
        ↓
synthetic_customer_daily.hpl
        ↓
persisted target rows
        ↓
audit_execution_finalize.hpl
        ↓
SUCCESS / FAILED
```

### 快速驗證

```bash
cp .env.example .env

python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet

make lifecycle-smoke
make supply-chain-smoke
```

`make supply-chain-smoke` 會真的：

1. Build v0.4 Hop runtime image。
2. 驗證 OCI provenance labels。
3. Candidate → TEST → PROD retag。
4. 驗證三者 image ID 完全一致。
5. 產生 CycloneDX image SBOM。
6. 建立 offline bundle。
7. 產生 SHA-256 與 detached signature。
8. 移除 local image references。
9. 從 archive `docker load`。
10. 再驗 loaded image ID。

### 啟動

```bash
docker compose --profile orchestration up -d --build
docker compose ps
```

- Airflow UI: `http://localhost:8080`
- Hop Server: `http://localhost:8181`
- PostgreSQL: `localhost:5432`
- DAG: `hop_synthetic_customer_daily`

> 所有 Sample Data、Hostname、Credential、Schema 與公司資訊均為 synthetic / generic。正式 Credential 不 bake 進 image。

詳細文件：

- `docs/ARCHITECTURE.md`
- `docs/ORCHESTRATION.md`
- `docs/AUDIT_LIFECYCLE.md`
- `docs/SUPPLY_CHAIN.md`
- `docs/SECURITY.md`
- `docs/GOVERNANCE.md`

## English

`enterprise-etl-platform` is an **Enterprise Data Engineering Platform** portfolio project covering ETL execution, Airflow orchestration, Apache Hop runtime, PostgreSQL audit, retry lifecycle management, software-supply-chain controls, air-gapped delivery, and observability.

### v0.4 — Immutable Supply Chain

v0.4 packages the Hop project into an immutable runtime image, records OCI provenance labels, enforces build-once promotion across candidate/TEST/PROD references, generates a CycloneDX image SBOM, and creates a signed/checksummed offline transfer bundle.

CI removes the local promoted image references, reloads the Docker archive, and proves the loaded image ID matches the original candidate. Production credentials remain runtime-injected and are not baked into the image.

### Quick validation

```bash
cp .env.example .env
python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
make lifecycle-smoke
make supply-chain-smoke
```

All sample data, hostnames, credentials, schemas, and company information are synthetic or generic.
