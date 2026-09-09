# Security / 安全

## 繁體中文

### v0.5 Security baseline

原有控制維持：

- Secret Scan
- Trivy filesystem scan
- Repository CycloneDX SBOM
- Image SBOM
- immutable image identity
- signed/checksummed offline bundle
- runtime credential injection

新增 observability controls：

1. SQL Exporter 經 `etl_observability` read-only views 取得資料。
2. Grafana 只讀 Prometheus，不直接讀 PostgreSQL。
3. Repository credential 全為 synthetic sample。
4. Alertmanager local receiver 不含外部 webhook/token。
5. Monitoring endpoints 在 production 應限制 private network / ingress。
6. Grafana production admin credential 必須外部注入。
7. Notification credential 應由 Secret manager 管理。
8. Metrics label 不應包含 customer payload、token、password、SQL text 或高基數敏感 identifier。

### Monitoring data sensitivity

即使 metrics 不含業務 payload，仍可能揭露：

- pipeline names
- environment
- failure rate
- execution frequency
- last-success time
- operational health

因此 production Prometheus/Grafana/Alertmanager 仍需：

- authentication
- authorization
- TLS
- retention policy
- backup policy
- network isolation

### Synthetic monitor identity

Repository migration 中的 `etl_monitor` / synthetic password 只供 portfolio/local CI。

正式環境應：

- 建立獨立 read-only monitoring identity
- password/credential 由 Secret 管理
- restrict CONNECT / schema usage / view SELECT
- 定期 rotation

### Alertmanager

`portfolio-null` receiver 故意不向外發送。

Slack、Teams、Email、PagerDuty 等 integration 不應在 repository 中保存真實 token/webhook。

## English

v0.5 preserves the existing repository, image, SBOM, signing, and runtime-secret controls while adding a monitoring security boundary.

SQL Exporter reads only aggregate observability views, and Grafana reads Prometheus rather than PostgreSQL directly. Production monitoring endpoints require authentication, TLS, network isolation, retention controls, and externally managed credentials.

Metric labels must not contain sensitive payloads, tokens, passwords, SQL text, or uncontrolled high-cardinality identifiers.

The repository monitoring identity and password are synthetic local examples only.
