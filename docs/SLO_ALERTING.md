# SLO & Alerting / SLO 與告警

## 繁體中文

### v0.5 SLO baseline

Enterprise ETL Platform v0.5 定義第一版可執行 SLO：

**ETL completed-attempt success ratio ≥ 99%**

Prometheus recording rule：

`etl:slo_success_ratio`

定義：

```text
SUCCESS completed attempts
---------------------------  >= 99%
SUCCESS + FAILED attempts
```

只有 final states `SUCCESS` 與 `FAILED` 進入 counter；`RUNNING` 不放入 counter，避免狀態轉換造成 counter decrease。

### Error budget

目標錯誤率：

`1% = 1 - 0.99`

Recording rules：

- `etl:slo_error_ratio`
- `etl:slo_error_budget_remaining`

Error budget remaining：

```text
1 - (current error ratio / allowed error ratio)
```

最低 clamp 到 0。

### Alert rules

#### ETLPipelineSLOBreach

條件：

`etl:slo_success_ratio < 0.99`

Severity：`warning`

用途：成功率低於 baseline。

#### ETLStaleRunningExecution

條件：

`etl_running_stale_total > 0`

Severity：`critical`

Stale 定義：execution 維持 `RUNNING` 超過 30 分鐘。

#### ETLNoRecentSuccess

條件：

`time() - etl_last_success_timestamp_seconds > 3600`

並要求 last success 已存在。

Severity：`warning`

`for: 5m`，避免短暫 scrape/clock boundary 造成立即告警。

### Alertmanager

v0.5 提供 Alertmanager baseline，但 portfolio/local receiver 是：

`portfolio-null`

它故意不向 Slack、Email、Teams 或 PagerDuty 發送訊息，以避免 repository 綁定真實 endpoint/token。

正式環境應依組織流程設定 receiver，並由 Secret 管理 notification credential。

### CI proof

`scripts/observability_smoke.sh` 會建立 synthetic execution：

- SUCCESS
- FAILED
- retry SUCCESS
- stale RUNNING

然後驗證：

1. SQL Exporter 有完整 ETL metrics。
2. Prometheus scrape 成功。
3. Recording rules 已載入。
4. `ETLPipelineSLOBreach` 實際 firing。
5. `ETLStaleRunningExecution` 實際 firing。
6. Alertmanager ready。
7. Grafana datasource 與 dashboard 已 provision。

因此 v0.5 的 alert 不是只有 YAML syntax，而有 runtime evaluation proof。

### Production evolution

此版本是 baseline，不代表所有企業 production SLO 都應直接使用 lifetime cumulative ratio。

正式環境可延伸為：

- rolling 30d availability
- 5m / 1h burn-rate alerts
- pipeline-specific SLO
- business-tier-specific thresholds
- maintenance window inhibition
- Alertmanager routing / silence / escalation
- external notification integration

這些可在後續治理版本強化。

## English

v0.5 defines an executable SLO baseline: completed ETL attempts should maintain a success ratio of at least 99%.

Only final SUCCESS and FAILED states participate in the monotonic execution counters. RUNNING state is represented through gauges such as stale-running count.

Prometheus recording rules calculate success ratio, error ratio, and remaining error budget. Alert rules cover SLO breach, stale RUNNING execution, and lack of a recent success.

The local Alertmanager receiver is intentionally a null receiver; production notification endpoints and credentials must be configured externally.

The CI observability smoke test creates synthetic successful, failed, retried, and stale executions and proves the metrics, rules, firing alerts, Alertmanager, Prometheus, and Grafana provisioning all work at runtime.
