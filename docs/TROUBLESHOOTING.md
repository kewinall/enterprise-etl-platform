# Troubleshooting / 疑難排解

## 繁體中文

### `docker compose config` 失敗

先確認 Docker Compose v2：

```bash
docker compose version
```

再確認 `.env` 是否由 `.env.example` 建立。

### PostgreSQL healthcheck 未通過

```bash
docker compose ps
docker compose logs postgres
```

檢查 `POSTGRES_DB`、`POSTGRES_USER` 與 `POSTGRES_PASSWORD` 是否一致。

### CI 文件驗證失敗

`scripts/validate_repository.py` 要求主要文件同時包含「繁體中文」與「English」區段，並阻擋已知非 generic token。

### Security workflow 失敗

先執行：

```bash
python scripts/secret_scan.py
```

若 Trivy 發現漏洞，應更新 dependency/base image 或建立有依據且具期限的 exception；不要直接關閉 security gate。

## English

### `docker compose config` fails

Confirm Docker Compose v2 is available and create `.env` from `.env.example`.

### PostgreSQL healthcheck fails

Use `docker compose ps` and `docker compose logs postgres`, then verify the PostgreSQL variables are consistent.

### Documentation validation fails

`scripts/validate_repository.py` requires the primary documentation set to contain both Traditional Chinese and English sections and rejects known non-generic tokens.

### Security workflow fails

Run the local secret policy scan first. For Trivy findings, update the affected dependency/base image or create a justified, time-bounded exception rather than disabling the security gate.
