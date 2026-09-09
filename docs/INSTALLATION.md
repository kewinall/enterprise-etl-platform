# Installation / 安裝

## 繁體中文

### 前置需求

- Docker Engine 24+ 或相容版本
- Docker Compose v2
- Python 3.12
- Git
- 建議至少 4 GB Docker memory；Airflow + Hop + PostgreSQL 建議更多

### Clone 與驗證

```bash
git clone https://github.com/kewinall/enterprise-etl-platform.git
cd enterprise-etl-platform
cp .env.example .env

python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
make lifecycle-smoke
```

### v0.3 lifecycle smoke

`make lifecycle-smoke` 會建立 temporary Docker network、PostgreSQL、Hop Server，並測試：

1. 套用 `001_etl_audit.sql` 與 `002_v0_3_audit_lifecycle.sql`。
2. attempt 1 寫入 RUNNING。
3. attempt 1 finalize FAILED。
4. attempt 2 寫入 RUNNING。
5. attempt 2 執行 synthetic ETL。
6. attempt 2 finalize SUCCESS。
7. 驗證 lifecycle events。
8. 驗證 target 有 3 筆資料。
9. 自動 cleanup。

### 新環境啟動

```bash
docker compose --profile orchestration up -d
docker compose ps
```

PostgreSQL 新 volume 第一次初始化時，會依序執行 `postgres/init/` 中的 SQL。

### 從 v0.2 local volume 升級

PostgreSQL official image **不會**在既有 data volume 上重新執行 `/docker-entrypoint-initdb.d`。

若要保留 v0.2 local data：

```bash
docker compose up -d postgres
docker compose exec -T postgres \
  psql -U etl_user -d etl_audit \
  < postgres/init/002_v0_3_audit_lifecycle.sql
```

如果只是 synthetic portfolio/test environment，也可重建：

```bash
docker compose down -v
docker compose --profile orchestration up -d
```

> `down -v` 會刪除 local PostgreSQL volume，只適用可丟棄的 synthetic/test data。

### 驗證 schema

```bash
docker compose exec postgres \
  psql -U etl_user -d etl_audit -c "\dt etl_audit.*"

docker compose exec postgres \
  psql -U etl_user -d etl_audit -c "\dt etl_data.*"
```

### Airflow

第一次 standalone 啟動：

```bash
docker compose logs airflow
```

取得 local login 後觸發：

`hop_synthetic_customer_daily`

## English

### Validation

Use `make lifecycle-smoke` to start temporary PostgreSQL and Hop Server containers and prove the complete v0.3 lifecycle, including a failed first attempt, a successful retry, append-only events, and three persisted target rows.

### Upgrading an existing v0.2 local volume

The PostgreSQL official image does not rerun `/docker-entrypoint-initdb.d` for an existing data volume. Apply `002_v0_3_audit_lifecycle.sql` manually if the data must be preserved.

For disposable synthetic/test environments, recreating the volume with `docker compose down -v` is acceptable.

Never use destructive volume removal for real production data.
