# Installation / 安裝

## 繁體中文

### 前置需求

- Docker Engine 24+ 或相容版本
- Docker Compose v2
- Python 3.12
- Git
- OpenSSL
- Connected build/test zone 首次需取得 container images

### Repository validation

```bash
git clone https://github.com/kewinall/enterprise-etl-platform.git
cd enterprise-etl-platform
cp .env.example .env

python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
make lifecycle-smoke
make observability-smoke
make supply-chain-smoke
```

### Monitoring stack

```bash
docker compose --profile monitoring up -d
docker compose ps
```

Endpoints：

- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`
- SQL Exporter: `http://localhost:9399/metrics`

Local synthetic Grafana credential 來自 `.env.example`，不得沿用到 production。

### Existing PostgreSQL volume upgrade

PostgreSQL init scripts只在新 data directory 執行。

若沿用 v0.4 local volume，需要套用：

```bash
docker compose up -d postgres

docker compose exec -T postgres \
  psql -U etl_user -d etl_audit \
  < postgres/init/003_v0_5_observability.sql
```

此 migration 建立 read-only observability views 與 synthetic sample monitor role。

正式環境應改由受控 migration / DBA 流程建立 monitoring identity，password 由 Secret manager 注入。

### Dashboard

Grafana 啟動後會自動 provision：

- Prometheus datasource
- `Enterprise ETL Operations` dashboard

### Observability smoke

```bash
make observability-smoke
```

Smoke test 使用 temporary Docker network，不依賴既有 Compose state；完成後會 cleanup。

### Air-Gapped note

v0.4 Hop runtime offline bundle 機制保持不變。

若 production Air-Gapped environment 也要部署 v0.5 monitoring stack，Prometheus / Alertmanager / Grafana / SQL Exporter image 應透過組織既有 image approval/mirroring 流程搬入，避免將所有第三方 image 無限制塞入 ETL runtime bundle。

## English

Use `docker compose --profile monitoring up -d` to start PostgreSQL plus SQL Exporter, Prometheus, Alertmanager, and Grafana.

For an existing v0.4 PostgreSQL volume, apply `003_v0_5_observability.sql` manually because PostgreSQL initialization scripts are not rerun for an existing data directory.

The Grafana datasource and Enterprise ETL Operations dashboard are provisioned automatically.

For air-gapped production monitoring, mirror and approve third-party monitoring images through the organization's image-supply process rather than embedding them into the ETL runtime archive.
