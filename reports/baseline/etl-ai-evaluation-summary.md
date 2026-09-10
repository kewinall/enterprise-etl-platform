# ETL AI Evaluation Baseline

## 繁體中文

| Evidence | Baseline |
|---|---:|
| Synthetic cases | 10 |
| Valid parser cases | 9 |
| Expected parse failures | 1 |
| Structural case exact match | 100% |
| Unexpected parsing failure | 0% |
| Semantic structured validity | 100% |
| Unsupported structured claims | 0 |
| Parser truth preservation | 100% |
| Provider token / cost | unavailable |

這些 headline 由 `tests/test_p2_evaluation.py` 針對目前 `evaluation/dataset.json` 重新計算後核對。**100% 只代表小型 synthetic regression corpus，不代表 production parser/model accuracy。**

Current-run parser/AI latency 由 GitHub Actions 產生並上傳 `p2-etl-ai-evaluation` artifact；不把某台 runner 的時間硬寫成永久 benchmark。

## English

The baseline is verified against the repository-owned synthetic dataset by regression tests. It is not customer data and not a production/provider benchmark. Token and cost remain unavailable until a live Multi-LLM AI Gateway response supplies usage and pricing evidence.
