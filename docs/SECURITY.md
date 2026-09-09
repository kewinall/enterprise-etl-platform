# Security / 安全

## 繁體中文

### v0.6 Security model

Repository security 現在分成四層：

1. Source / secret controls
2. ETL AI context boundary
3. Vulnerability remediation lifecycle
4. Immutable environment promotion

既有 Trivy、SBOM、signed/checksummed air-gapped bundle、runtime credential injection、read-only observability boundary 全部保留。

### ETL Intelligence security

Deterministic parser 可以讀取結構，但 AI context builder 只輸出 allowlisted normalized metadata。

控制：

- connection config 不進 AI context
- password / secret / token / credential key redaction
- SQL string literal redaction
- AI output 必須使用 structured contract
- factual commentary 必須引用 evidence_refs
- unknown SQL ID / step / dependency 直接拒絕
- parser truth 與 AI result 分離
- AI unavailable / invalid result fail-safe 到 deterministic fallback

### Vulnerability remediation

Scanner finding 必須經 applicability validation，不能只靠版本字串。

Gate 支援的 evidence decision：

- remediated
- not-applicable + evidence
- vendor-backport + advisory
- risk-accepted + approval reference

Linux / Python / Container / Base Image 的 synthetic examples 與 regression test 位於 samples/security 與 tests/test_vulnerability_management.py。

### GitLab enterprise delivery

Root .gitlab-ci.yml 展示：

- validation / tests
- Secret Scan
- repository + image Trivy
- CycloneDX SBOM
- CVE lifecycle gate
- immutable candidate
- TEST digest verification
- manual serialized PROD promotion

PROD 不重新 build。

### Observability security

Monitoring 仍經 etl_observability read-only surface。Grafana 不直接讀 raw PostgreSQL audit table；production endpoints 必須有 authn/authz、TLS、private-network controls 與 retention policy。

## English

v0.6 preserves the existing secret, Trivy, SBOM, signing, air-gapped, runtime-secret, and observability controls while adding an allowlisted AI context boundary, evidence-bound semantic output, remediation-driven vulnerability gating, and same-digest enterprise promotion.

The AI layer is fail-safe: invalid semantic output never changes deterministic parser truth.

Production GitLab deployments should use protected/masked variables, protected environments, authorized approvers, and registry digest identity.
