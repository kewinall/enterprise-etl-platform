# Installation / 安裝

## 繁體中文

### 前置需求

- Docker Engine 24+ 或相容版本
- Docker Compose v2
- Python 3.12（Repository validation/test）
- Git
- 建議至少 4 GB 可用 Docker memory；啟動 Airflow 時建議更多

### Clone 與 Repository validation

```bash
git clone https://github.com/kewinall/enterprise-etl-platform.git
cd enterprise-etl-platform
cp .env.example .env

python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
```

### Hop-only executable smoke test

此測試會實際啟動 `apache/hop:2.19.0` Hop Server，透過 REST API 執行 `synthetic_customer_daily.hpl`，完成後自動移除測試 container。

```bash
make hop-smoke
```

或：

```bash
bash scripts/hop_api_smoke.sh
```

### 啟動 Airflow + Hop integration

```bash
docker compose --profile orchestration up -d
docker compose ps
```

服務：

| Service | Local endpoint |
|---|---|
| Airflow | `http://localhost:8080` |
| Hop Server | `http://localhost:8181` |
| PostgreSQL | `localhost:5432` |

Airflow 使用 `standalone` 作為 v0.2 local portfolio runtime。第一次啟動後：

```bash
docker compose logs airflow
```

取得 local login，登入 Airflow 後手動觸發：

`hop_synthetic_customer_daily`

### 單獨啟動 Hop Server

```bash
docker compose --profile etl up -d hop
docker compose logs -f hop
```

### 關閉

```bash
docker compose --profile orchestration down
```

> `.env.example` 的 Credential 僅供 synthetic local demo。正式環境應由 Secret store / Vault / Kubernetes Secret 或等價機制注入。

## English

### Prerequisites

- Docker Engine 24+ or compatible
- Docker Compose v2
- Python 3.12 for repository validation/tests
- Git
- At least 4 GB of Docker memory is recommended; Airflow may require more

### Validate the repository

Use the clone and validation commands above. `make hop-smoke` starts the pinned Apache Hop Server image, executes the real `synthetic_customer_daily.hpl` pipeline through the REST endpoint, validates the response, and removes the temporary container.

### Start Airflow + Hop

```bash
docker compose --profile orchestration up -d
docker compose ps
```

Airflow runs in standalone mode for this local portfolio baseline. Read `docker compose logs airflow` for the generated local login, then trigger `hop_synthetic_customer_daily`.

The credentials in `.env.example` are synthetic local defaults only. Production credentials must be injected through an appropriate secret-management mechanism.
