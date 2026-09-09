# Installation / 安裝

## 繁體中文

### 前置需求

- Docker Engine 24+ 或相容版本
- Docker Compose v2
- Python 3.12（僅 Repository validation/test 需要）
- Git

### 本機驗證

```bash
git clone https://github.com/kewinall/enterprise-etl-platform.git
cd enterprise-etl-platform
cp .env.example .env
python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet
```

### 啟動 PostgreSQL Audit baseline

```bash
docker compose up -d postgres
docker compose ps
```

### Optional profiles

v0.1 將 Airflow 與 Hop 放在 Compose profiles 中，避免僅做 schema/CI 驗證時不必要地拉取大型 image。

```bash
docker compose --profile orchestration --profile etl up -d
```

## English

### Prerequisites

- Docker Engine 24+ or compatible
- Docker Compose v2
- Python 3.12 for repository validation/tests
- Git

Use the commands above to validate the repository and start the PostgreSQL audit baseline. Airflow and Hop are intentionally placed behind optional Compose profiles in v0.1 so lightweight validation does not require pulling large runtime images.
