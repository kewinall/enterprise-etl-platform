# ETL Intelligence / ETL 設計期智慧分析

## 繁體中文

### 定位

v0.7 的 ETL Intelligence 是 **Legacy ETL Modernization 的 semantic layer**，不是 structural truth engine。

核心原則：

- Deterministic parser = structural truth
- Normalized metadata = ETL domain contract
- Migration validator = correctness evidence
- AI semantic analyzer = evidence-bound commentary
- Multi-LLM AI Gateway = preferred model control plane

### Supported deterministic inputs

- Apache Hop XML: `.hpl / .hwf / .xml`
- synthetic generic legacy JSON
- synthetic Pentaho transformation: `.ktr`
- synthetic Pentaho job: `.kjb`

Pentaho support 是 public reference parser，不宣稱涵蓋所有 proprietary plugin。

### Normalized metadata v1.1

包含 Pipeline、Step、Source、Target、Table、Column/Field declaration、SQL、Step dependency、Workflow dependency、Connection reference、Parameter、Variable、Evidence locator、source SHA-256、Lineage classification 與 Capability boundary。

### Lineage authority

`lineage.structural`：explicit artifact facts。  
`lineage.inferred`：由 explicit graph path 或保守 SQL table reference deterministic 推導。  
`lineage.ai_interpretation`：保留為空的 truth contract；AI interpretation 存在 semantic result，不得冒充 deterministic lineage。

完整說明見 `docs/METADATA_LINEAGE.md`。

### Migration assistance

`MigrationPlanner` 將元件分類為：

- direct
- direct-with-validation
- manual-review
- manual-required

`MigrationValidator` deterministic 比對 source/target tables、SQL digest、parameter、variable 與 named step preservation。AI 不參與 PASS/FAIL。

~~~bash
python scripts/migration_case.py   samples/pentaho_to_hop/legacy_order_enrichment.ktr   --target samples/pentaho_to_hop/hop_order_enrichment.hpl
~~~

### AI boundary and Gateway

只有 filtered normalized metadata 可進入 LLM。Connection credential 不傳入；SQL literal 會 redaction；variable value 不傳入。

Portfolio reference architecture 使用：

~~~text
ETL Intelligence
      |
      v
OpenAICompatibleGatewayClient
      |
      v
Multi-LLM AI Gateway
      |
OpenAI / Anthropic / Gemini / Local
~~~

Gateway 負責 model routing、fallback、provider abstraction、authentication、policy、budget/cost。ETL repo 不重新實作這些能力。

Local tests 可直接注入 mock callable，確保 unit test 與 deterministic correctness 不依賴 LLM。

### Failure modes

- LLM unavailable → fallback，parser truth 仍可用。
- LLM 回傳 unknown evidence / SQL / dependency → reject + fallback。
- unsupported legacy component → manual-required。
- uncertain join / variable scope → manual-review。
- column lineage 不可證明 → capability boundary，不做過度宣稱。

### Responsibility boundary

ETL Intelligence 不負責 runtime Incident RCA；DataOps Copilot 才負責 incident reasoning。ETL repo 也不實作 MCP transport、RAG retrieval 或 model routing。

## English

v0.7 treats ETL Intelligence as the semantic layer of a deterministic modernization workflow.

Pentaho KTR/KJB and Apache Hop artifacts become normalized metadata v1.1. Structural lineage, deterministic inference, and AI interpretation are explicitly separated. The migration validator remains deterministic; AI never decides migration correctness.

The preferred LLM path is the portfolio Multi-LLM AI Gateway through an OpenAI-compatible adapter. The ETL repository does not duplicate routing, fallback, provider, authentication, or cost-governance responsibilities.
