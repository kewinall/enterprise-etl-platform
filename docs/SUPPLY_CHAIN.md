# Supply Chain & Offline Promotion / 供應鏈與離線升版

## 繁體中文

### Existing immutable baseline

v0.4 建立以下 invariant：

Build once → identify → TEST → approve → promote same image → PROD

PROD 不重新 build。

Runtime image 由 docker/hop-runtime.Dockerfile 建立，OCI labels 保留 version / revision / source。Offline bundle 包含 image archive、CycloneDX SBOM、manifest、SHA256SUMS、signature 與 public key material。

### v0.6 Registry digest promotion

v0.6 將 local image-ID proof 延伸成 registry digest reference implementation：

- scripts/registry_promote.sh
- scripts/verify_image_digest.sh
- root .gitlab-ci.yml

scripts/registry_promote.sh 會 pull source、取得 RepoDigest、tag/push target、pull target，再比較 source / target digest。

Production identity 應使用 repo@sha256:...，而不是 mutable tag。

### Vulnerability-driven rebuild

如果 CVE remediation 需要 package / dependency / base image 變更：

1. 修改 source definition。
2. 產生新的 immutable candidate。
3. 重新生成 SBOM。
4. 重新執行 Trivy / vulnerability gate。
5. 重跑 regression tests。
6. TEST 驗證。
7. approval。
8. promote same new digest 到 PROD。

不得在 PROD image 原地 patch。

### Air-Gapped bundle

既有流程保留：

signed bundle
→ verify detached signature
→ verify SHA-256
→ unpack
→ verify inner checksums/signature
→ docker load
→ compare loaded image identity
→ inject runtime configuration
→ deploy

離線 rollback 也使用先前已批准的 bundle / digest，不重新 build。

## English

v0.6 extends the v0.4 immutable and air-gapped supply-chain controls with registry-digest promotion.

The enterprise rule is build once, scan, generate SBOM, remediate if necessary, validate in TEST, approve, and promote the same digest into PROD.

Any remediation that changes the artifact produces a new candidate and repeats the full lifecycle. PROD is never patched or rebuilt in place.
