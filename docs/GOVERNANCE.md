# ETL Lifecycle & Deployment Governance / ETL 生命週期與部署治理

## 繁體中文

### Lifecycle

`Design → Develop → Validate → Lifecycle Smoke → Security Scan → Build → TEST → Approve → Promote → PROD → Observe → Audit`

### v0.4 promotion rule

最重要規則：

**Build once. Promote the same artifact. Never rebuild for PROD.**

允許：

```text
candidate sha256:X
      ↓
TEST sha256:X
      ↓
PROD sha256:X
```

不允許：

```text
candidate sha256:X
      ↓
TEST sha256:X
      ↓
rebuild
      ↓
PROD sha256:Y
```

`scripts/promote_image.sh` 會在 promotion 前後比較 image ID，不一致即失敗。

### Source-to-artifact traceability

Runtime image OCI labels保存：

- platform version
- source revision
- source repository

Offline `manifest.json` 再保存：

- source commit
- image reference
- image ID
- archive name
- SBOM name
- promotion policy

### Retry governance

v0.3 execution governance 保持：

- 每個 retry 是獨立 attempt。
- `RUNNING → SUCCESS`
- `RUNNING → FAILED`
- Retry 不覆寫舊失敗歷史。
- Target rows 保存 execution identity。

### Environment separation

| Environment | Artifact policy | Configuration policy |
|---|---|---|
| DEV | 可 build candidate | synthetic/local config |
| TEST | 使用 candidate immutable identity | TEST runtime config |
| PROD | 只能 promote 已核准 identity | PROD secret/runtime config |

### Air-Gapped transfer

離線交付必須包含：

- image archive
- CycloneDX image SBOM
- manifest
- SHA-256 checksums
- detached signature

Offline target 必須先 verify，再 `docker load`。

### Release gate

Tag / Release 只在**同一 main commit**的 CI 與 Security 成功後建立。

v0.4 main CI 另外會產生 validated `offline-bundle` artifact，Release workflow 下載該 artifact 並附加到 GitHub Release。

## English

v0.4 formalizes build-once promotion governance: candidate, TEST, and PROD must reference the exact same immutable image identity. Rebuilding for production is a policy violation.

OCI labels and the offline manifest connect the image back to the source revision. The air-gapped transfer contains the image archive, SBOM, manifest, checksums, and signatures.

The release gate still requires successful CI and Security for the same main commit, and the validated CI offline bundle is attached to the GitHub Release.
