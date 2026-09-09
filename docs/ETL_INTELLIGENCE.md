# ETL Intelligence / ETL 設計期智慧分析

## 繁體中文

### 定位

v0.6 將平台從 runtime/audit/observability 延伸到 design-time ETL intelligence，但責任仍屬於 Enterprise Data Engineering Platform。

核心原則：

Deterministic parser = structural truth  
AI semantic analyzer = semantic commentary

AI 不解析原始 ETL artifact，也不覆寫 parser truth。

### Data flow

Legacy ETL / Apache Hop
→ Deterministic ETL Parser
→ Normalized Metadata
→ Sensitive-data filtering
→ AI Semantic Analyzer
→ Evidence-bound ETL Intelligence

Normalized Metadata 包含：

- Pipeline / Workflow
- Step
- Hop / Dependency
- SQL
- Source / Target
- Table
- Field
- Connection reference
- Provenance / source SHA-256
- Evidence locator

### Deterministic parsing

目前 reference implementation 支援：

- Apache Hop XML: .hpl / .hwf / generic XML root
- synthetic generic legacy ETL JSON

Parser 只做可重現的結構抽取，不猜測商業語意。

執行：

~~~bash
python scripts/etl_intelligence.py parse   samples/etl_intelligence/generic_order_enrichment.json   --output /tmp/metadata.json
~~~

### AI boundary

只有 normalized metadata 可以進入 AI context。Connection credential 不傳入；SQL string literal 會被 redaction。

AI output 必須：

- 使用固定 structured contract
- 引用 parser 產生的 evidence_refs
- SQL explanation 只能引用已存在 sql_id
- dependency explanation 只能引用已存在 step
- 不得新增不存在的 table / field / dependency
- 保留 parser_truth_digest

任何 contract violation 都會被拒絕並降級成 deterministic fallback。

### AI unavailable fallback

未設定 AI client 時仍可輸出：

- pipeline step count
- step type summary
- deterministic dependency summary
- SQL presence
- warning / provenance

因此 design-time inspection 不依賴 LLM availability。

### Provenance and evidence

Parser output 包含 source SHA-256 與每一個 extracted fact 的 locator。AI result 只保留解釋，不成為 structural source of truth。

### Portfolio responsibility boundary

本功能只回答 ETL design-time 問題：

- pipeline summary
- business logic explanation
- SQL explanation
- source → target interpretation
- dependency summary
- migration assistance

不負責 runtime incident RCA；runtime RCA 仍屬於 agentic-dataops-copilot 的責任範圍。

## English

v0.6 introduces design-time ETL intelligence while preserving the repository boundary as an Enterprise Data Engineering Platform.

The deterministic parser is the authoritative source for structure. The AI analyzer receives only normalized, filtered metadata and may produce semantic commentary. It cannot mutate parser truth.

AI output is schema-bound, evidence-bound, and validated against known parser evidence, SQL IDs, and dependency nodes. Invalid or unavailable AI output falls back to deterministic summaries.

This feature intentionally excludes runtime incident RCA.
