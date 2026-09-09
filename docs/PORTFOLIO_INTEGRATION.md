# Portfolio Integration / 作品集整合邊界

## 繁體中文

P1 將 ETL Intelligence 接到既有 portfolio layers，但不複製其責任。

~~~text
Legacy ETL
   |
   v
enterprise-etl-platform
Parser / Metadata / Migration / Lineage
   |
   +------------------> JSON knowledge/doc artifact --> enterprise-rag-platform
   |
   +--> data-platform-mcp-server
   |      read-only ETL metadata tools
   |                 |
   |                 +--> agentic-dataops-copilot
   |
   '--> Semantic Analyzer --> multi-llm-ai-gateway --> Providers
~~~

### Responsibility boundary

| Repository | Owns | Does not own in P1 |
|---|---|---|
| enterprise-etl-platform | ETL parser, normalized metadata, migration analysis, lineage truth, validation | MCP transport, RAG retrieval, incident RCA, model routing |
| data-platform-mcp-server | governed read-only access contract, MCP protocol, auth/scope/audit | parsing Pentaho/Hop, creating lineage truth |
| enterprise-rag-platform | knowledge ingestion/retrieval/grounding/evaluation | ETL structural parser |
| agentic-dataops-copilot | runtime incident evidence correlation/RCA/governed actions | design-time ETL migration correctness |
| multi-llm-ai-gateway | provider abstraction/routing/fallback/policy/cost/auth | ETL parser or migration validator |

### RAG reference integration

RAG 可 ingest：

- `docs/PENTAHO_TO_HOP_MIGRATION.md`
- `docs/METADATA_LINEAGE.md`
- architecture / runbook / generated semantic description
- exported metadata summary

但 RAG answer 不能改寫 ETL parser truth。

### DataOps reference integration

DataOps Copilot 優先透過 MCP Server 取得 pipeline metadata、dependencies、lineage 與 execution context。ETL Intelligence 不接管 Incident RCA。

### Multi-LLM reference integration

`etl_intelligence.gateway.OpenAICompatibleGatewayClient` 使用 Gateway 的 `/v1/chat/completions` contract。Routing、fallback、provider credentials、budget、cost、policy 都留在 Gateway。

Local unit test 仍可注入 mock callable，讓 deterministic test 不依賴外部 LLM。

## English

P1 connects the ETL domain producer to the portfolio integration, knowledge, operations, and model-control layers without duplicating their responsibilities.

The ETL repository owns parser truth, migration analysis, lineage classification, and deterministic validation. MCP owns governed access, RAG owns knowledge retrieval, DataOps owns incident reasoning, and the AI Gateway owns model routing and provider governance.
