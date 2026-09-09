# Pentaho → Apache Hop Migration Case / Pentaho → Apache Hop 遷移案例

## 繁體中文

本案例完全使用 synthetic artifact，不含任何客戶 Job、帳密、內部 URL 或真實業務資料。

### Case flow

~~~text
Pentaho KTR / KJB
      |
Deterministic Parser
      |
Normalized Metadata v1.1
      |
Compatibility / Migration Planner
      |
Apache Hop Target Design
      |
Deterministic Validation
      |
Representative data reconciliation
~~~

範例：

- `samples/pentaho_to_hop/legacy_order_enrichment.ktr`
- `samples/pentaho_to_hop/legacy_daily_orders.kjb`
- `samples/pentaho_to_hop/hop_order_enrichment.hpl`

代表性元件包含 Table Input、SQL、Filter Rows、Database Lookup、Calculator、Merge Join、Table Output、Job → Transformation dependency、Parameter 與 Variable。

### Mapping policy

| Legacy component | Hop target | Disposition |
|---|---|---|
| TableInput | Table Input | direct |
| FilterRows | Filter Rows | direct |
| DatabaseLookup | Database Lookup | direct-with-validation |
| Calculator | Calculator | direct-with-validation |
| SelectValues | Select Values | direct |
| TableOutput | Table Output | direct |
| MergeJoin | Merge Join | **manual-review** |
| TRANS / JOB | Pipeline / Workflow action | **manual-review** |
| Unknown plugin | none | **manual-required** |

「direct」不代表不需要測試；只代表可以建立明確 deterministic mapping。Join ordering、null semantics、data type coercion、plugin behavior、database-specific SQL 等仍需驗證。

### SQL / connection / parameter / variable

- SQL 先保留原文與 digest，修改 SQL 後不得只靠 AI 判斷等價。
- Connection 只保留 metadata reference；credential 必須由 environment / secret management 注入。
- Parameter 名稱與 default 需保留並比對。
- Variable 需保留名稱並人工確認 scope、late binding 與 environment precedence。
- Dynamic SQL、runtime-resolved object name 不宣稱可完全自動遷移。

### Workflow dependency

KJB 中的 Transformation / Job reference 會產生 `kind=pipeline` 的 structural dependency，與 step hop 分開保存。Migration plan 必須保留這些依賴；AI 不得新增不存在的 workflow edge。

### Correctness gates

1. source SHA / parser evidence 不可被 AI 修改；
2. source / target table 集合 deterministic reconciliation；
3. SQL digest 或明確 reviewed change；
4. parameter / variable / workflow dependency preservation；
5. representative input/output row count、key、aggregate、null distribution reconciliation；
6. production promotion 前仍需 human review。

執行：

~~~bash
python scripts/migration_case.py   samples/pentaho_to_hop/legacy_order_enrichment.ktr   --target samples/pentaho_to_hop/hop_order_enrichment.hpl

bash scripts/p1_integration_smoke.sh
~~~

### AI boundary

AI 可以提供 migration recommendation、商業邏輯說明與風險提示，但 **不能成為 migration PASS/FAIL 的唯一 correctness mechanism**。Parser truth、migration validator、test fixtures、data reconciliation 與 review 才是 release gate。

## English

This public synthetic case demonstrates a Pentaho-to-Hop modernization path without using any customer artifact.

The deterministic parser extracts KTR/KJB structure into normalized metadata. The migration planner classifies direct mappings versus review-required components. Validation compares source/target tables, SQL digests, parameters, variables, and named steps without using AI.

AI may explain or recommend migration actions, but it is advisory only. Structural truth, deterministic validation, representative data reconciliation, and human review remain the correctness mechanisms.
