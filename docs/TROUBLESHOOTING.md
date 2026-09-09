# Troubleshooting / 疑難排解

## 繁體中文

### `docker compose config` 失敗

```bash
docker compose version
cp .env.example .env
docker compose config
```

確認使用 Docker Compose v2。

### `make hop-smoke` 無法連線

先確認 Docker 可正常 pull/run：

```bash
docker pull apache/hop:2.19.0
docker ps
```

查看 smoke container log：

```bash
docker ps -a | grep enterprise-etl-hop-smoke
```

CI/script 結束時會自動 cleanup；若人工中止，可手動移除殘留 container。

### Hop Server 回傳 401 / 403

確認：

- `HOP_SERVER_USER`
- `HOP_SERVER_PASS`
- Airflow container 取得的環境變數

```bash
docker compose exec airflow env | grep '^HOP_'
```

不要把正式 password 寫回 Repository。

### Airflow DAG 看不到

```bash
docker compose logs airflow
docker compose exec airflow airflow dags list
```

確認 `airflow/dags/hop_synthetic_customer_pipeline.py` 已 mount 到 `/opt/airflow/dags`。

### Hop pipeline 執行失敗

```bash
docker compose logs hop
```

確認：

- Hop image 為 2.19.0
- `/files/project/project-config.json` 存在
- `/files/project/pipelines/synthetic_customer_daily.hpl` 存在
- `HOP_PIPELINE_PATH` 在 Airflow 中仍為 `${PROJECT_HOME}/pipelines/synthetic_customer_daily.hpl`

### Security workflow 失敗

先執行：

```bash
python scripts/secret_scan.py
```

Trivy 發現問題時應更新 dependency/base image 或建立具依據且有期限的 exception，不應直接停用 security gate。

## English

### Docker Compose validation fails

Confirm Docker Compose v2 is installed and create `.env` from `.env.example`.

### Hop smoke test cannot connect

Verify Docker can pull and run `apache/hop:2.19.0`. The smoke script starts a temporary Hop Server and cleans it up automatically.

### Hop Server returns 401/403

Check `HOP_SERVER_USER` and `HOP_SERVER_PASS` in the runtime environment. Never commit production passwords.

### Airflow DAG is missing

Inspect Airflow logs and run `airflow dags list` inside the container. Confirm the DAG bind mount is available.

### Hop execution fails

Inspect `docker compose logs hop`, confirm the project configuration and `.hpl` file exist, and ensure the pipeline path still uses `${PROJECT_HOME}`.

### Security workflow fails

Run the local secret-policy scanner first. Remediate Trivy findings or document a justified, time-bounded exception rather than disabling the security gate.
