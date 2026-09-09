# ETL Metadata & Lineage / ETL Metadata 與血緣

## 繁體中文

### Normalized metadata v1.1

`enterprise-etl-platform` 是 ETL domain truth producer。Parser output 可包含：

- Pipeline / Workflow
- Step
- Source / Target
- Table
- Column / Field declaration
- SQL
- Step dependency
- Pipeline / Workflow dependency
- Connection reference
- Parameter / Variable
- Evidence locator + source SHA-256
- Lineage classification
- Capability boundary

### Three lineage classes

| Class | Meaning | Authority |
|---|---|---|
| **structural** | artifact 中直接存在的 step hop、read/write attachment、workflow reference | deterministic parser truth |
| **inferred-deterministic** | 由 explicit graph path 或保守 SQL table reference 推導 | deterministic derivation，但必須標示 inferred |
| **AI interpretation** | business meaning / migration explanation / semantic hypothesis | commentary only，不得冒充 lineage truth |

~~~text
Pipeline
  |
  +-- structural: table -> step -> step -> target
  |
  +-- inferred-deterministic: source table ==> target table
  |
  '-- AI interpretation: "likely customer enrichment"
~~~

### Column-level boundary

目前 reference implementation **不宣稱完整 column-level lineage**。只有 artifact 明確提供 field mapping 時，才保留 structural field declaration。

下列情境不會被假裝成 deterministic column lineage：

- `SELECT *` wildcard expansion
- nested SQL expression / CASE / UDF
- dynamic SQL
- runtime-resolved schema/table
- stored procedure side effect
- vendor plugin opaque transform
- implicit type conversion

若要提升到 production-grade column lineage，應導入 dialect-aware SQL AST、catalog schema expansion、plugin-specific parser 與 regression corpus，再把結果標示為 structural 或 inferred。

### Export contract

ETL metadata 可由 producer 匯出成 JSON artifact；MCP Server 只讀取這個 contract，不重新解析 Pentaho/Hop。這避免 MCP protocol layer 成為第二份 ETL truth。

## English

Normalized metadata v1.1 separates structural lineage, deterministic inference, and AI interpretation.

Structural lineage is directly backed by artifact evidence. Deterministic inference is derived from explicit graph paths or conservative SQL references and is labeled as inferred. AI interpretation remains separate commentary.

The project intentionally does not claim complete column-level lineage for wildcard SQL, dynamic SQL, opaque plugins, runtime-resolved objects, or complex expressions.
