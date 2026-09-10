# ETL AI Evaluation / ETL AI 評測與 Production Evidence

## 繁體中文

### 目標

P2 不再以 Feature 數量作為成熟度指標，而是回答：**ETL AI 是否有效、可靠、可控，而且有可重複的 Evidence？**

評測資料全部位於 `evaluation/`，僅使用 synthetic / generic ETL，不包含任何客戶或 production data。

~~~text
Synthetic Evaluation Dataset
          |
          v
Deterministic Parser
          |
          +--> Structural Metrics
          |
          v
Normalized Metadata / Evidence
          |
          v
AI Semantic Analyzer
          |
          +--> Structured Validation
          +--> Unsupported-Claim Check
          +--> Gateway Usage / Cost / Latency
          |
          v
JSON + Markdown + Interactive HTML
~~~

### Engineering Decision — Deterministic First

**Structural truth 必須由 deterministic code 產生，AI 只能做 semantic enrichment。**

- Step / source / target / dependency / SQL / table 可由 parser 重複驗證，不需要模型猜測。
- AI output 必須引用 parser `evidence_refs`，source / target / dependency / SQL identifier 不能超出 parser truth。
- AI 無法使用時，metadata、lineage、migration validation 與 runtime 仍可工作。
- Invalid structured output 可做有限 validation retry；provider timeout、429、routing/fallback 仍由 Multi-LLM AI Gateway 負責。

Trade-off：

- Parser coverage 必須靠 fixture / regression test 擴充。
- Structured unsupported-claim detection 能攔截不存在的 entity reference，但**不是通用自然語言 fact checker**。
- Synthetic corpus 的高分只代表這組 regression corpus，不代表 production accuracy。

### Evaluation Dataset

P2 baseline 共 10 cases：

1. simple extraction
2. join
3. lookup
4. filter
5. aggregation
6. SQL-heavy transformation
7. multi-pipeline dependency
8. invalid / partial ETL definition
9. unsupported component
10. complex parameter usage

Ground truth 與 artifact 一起 version-control，涵蓋 steps、sources、targets、dependencies、SQL、tables、parameters/variables、unsupported components 與 expected parse failure。

### Parser Accuracy

~~~bash
python scripts/evaluate_etl_ai.py --stable --output-dir reports/generated
~~~

Metrics 從 repository dataset 實際比對產生：

- precision / recall / F1
- exact-match rate
- observed parsing failure rate
- unexpected parsing failure rate

`invalid_partial` 是預期失敗，因此 observed failure 與 unexpected failure 分開計算。

> 若 synthetic regression corpus 得到 100%，只能解讀為 parser 對這 10 個 checked-in cases 完全符合 ground truth；不得解讀成真實 Pentaho/Hop universe 的 100% accuracy。

### AI Semantic Evaluation

AI quality 量測：

- structured output validity
- factual consistency
- grounding
- completeness
- semantic usefulness proxy
- unsupported structured claim count
- parser truth preservation

CI 使用 `SyntheticEvidenceClient` 驗證 contract / guardrail，**不是 LLM provider/model benchmark**。真實模型品質比較必須以 `--live-gateway` 明確執行並保存結果。

### Hallucination / Unsupported Claim

`validate_ai_result()` 會拒絕 unknown evidence reference、unknown SQL id、unknown source、unknown target 與 unknown dependency endpoint。

~~~text
AI claim
   |
compare structured refs with parser evidence
   |
unsupported
   |
validation retry -> reject/fallback
~~~

### Failure Semantics

| Failure | ETL Intelligence behavior | Ownership |
|---|---|---|
| AI unavailable | parser metadata 保留；semantic enrichment = fallback | ETL domain |
| Invalid JSON / contract | 有限 validation retry，仍失敗則 reject/fallback | ETL domain |
| Unsupported structural claim | reject/fallback，不污染 parser truth | ETL domain |
| Provider timeout / 429 | ETL 不重新實作 routing；transport failure 直接降級 | Multi-LLM AI Gateway |
| Gateway provider fallback | 消費 Gateway attempts/provider/model evidence | Multi-LLM AI Gateway |

### Cost / Token / Latency

`OpenAICompatibleGatewayClient` 會保留 Gateway response 的：

- `usage.prompt_tokens`
- `usage.completion_tokens`
- `gateway.provider`
- `gateway.model`
- `gateway.cost_usd`
- `gateway.pricing_known`
- `gateway.attempts`

Report 提供 per-pipeline、batch、per-provider/model 聚合，以及 243 pipelines 線性 projection。

**若 Gateway 沒有實際 usage/pricing evidence，token/cost 必須是 `null`。** 不用字數假裝 token、不假設 provider price。

~~~bash
export ETL_AI_GATEWAY_URL=https://gateway.example.invalid
export ETL_AI_GATEWAY_API_KEY=replace-me
export ETL_AI_MODEL=default
python scripts/evaluate_etl_ai.py --live-gateway --output-dir reports/live
~~~

### Comparison / Ablation

每次 evaluation 都記錄：

- Parser-only structural exact match
- Parser + AI parser-truth preservation
- deterministic parser repeatability
- raw artifact bytes
- structured AI context bytes
- structured/raw byte ratio

比值不預設 structured metadata 一定更小。CI 不把 raw ETL 直接送 provider 來製造 token/cost 比較；真正 Raw ETL → LLM provider ablation 必須是明確 live experiment 並保存 usage evidence。

### Evidence Locations

| Evidence | Location |
|---|---|
| Dataset / ground truth | `evaluation/dataset.json`, `evaluation/cases/` |
| Evaluation engine | `etl_intelligence/evaluation.py` |
| Runner | `scripts/evaluate_etl_ai.py` |
| Regression / failure tests | `tests/test_p2_evaluation.py` |
| Checked-in summary | `reports/baseline/` |
| Current-run timing | GitHub Actions artifact `p2-etl-ai-evaluation` |
| Interactive portfolio story | `docs/enterprise-etl-platform-guide.html` |

## English

P2 turns ETL Intelligence into an evidence-oriented capability. Structural facts remain deterministic and version-controlled; semantic analysis remains optional and evidence-bound. The repository measures parser accuracy, structured semantic quality, failure semantics, repeatability, input-surface ablation, and—when supplied by the Multi-LLM AI Gateway—actual provider/model token, cost, attempt, and latency evidence.

The public baseline is synthetic. A perfect score on this regression corpus is not presented as a production benchmark, and unavailable provider usage is represented as `null` rather than estimated or fabricated.
