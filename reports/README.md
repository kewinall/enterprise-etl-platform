# Evaluation Reports / 評測報告

## 繁體中文

- `baseline/etl-ai-evaluation-summary.json`：machine-readable headline；unit test 會用目前 dataset 重算核對。
- `baseline/etl-ai-evaluation-summary.md`：人類可讀摘要。
- `baseline/etl-ai-evaluation-summary.html`：Interactive Portfolio visualization。
- GitHub Actions 每次執行 `scripts/evaluate_etl_ai.py`，並上傳 `p2-etl-ai-evaluation` artifact；該 artifact 包含當次 runner 實際 parser / AI latency。

沒有 Multi-LLM AI Gateway usage/pricing evidence 時，token/cost 保持 `null`。

## English

The checked-in baseline contains reproducible synthetic-regression claims. CI generates a fresh JSON/Markdown/HTML report with current-run timing and uploads it as the `p2-etl-ai-evaluation` artifact. Provider token/cost fields remain null unless actually supplied by the Gateway contract.
