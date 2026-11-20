# llm-api-contract

> 离线 API 契约检查器（v0.1）：把 LLM API 的终止事件、失败原因、usage、首 token 定义做成可测试的 contract。
> 研究线：**API 协议语义与评测测量效度**。
> 代码 DOI: https://doi.org/10.5281/zenodo.24399656

## 这是什么

- `docs/API-CONTRACT-PREREG.md`：预注册（看什么/怎么算/什么算异常）；
- `docs/CONTRACT-SPEC.md`：逐调用记录字段；
- `contract_tests/checker.py`：5 条离线检查；
- `contract_tests/test_contract.py`：pytest 用例；
- `scripts/run_contract_check.py`：读 JSONL 输出违规摘要。

## 不做什么

- 不调用模型 API；
- 不包含 prompt/题面/答案/raw 输出；
- 不做模型能力排名；
- 不宣称“官方已修复”。

## 快速开始

```bash
python -m pytest -q
python scripts/run_contract_check.py fixtures/records.jsonl
```

## 契约（v0.1）

| 编号 | 检查 |
|---|---|
| C1 | 声明有终止事件 → 必须有终止事件类型 |
| C2 | 无终止事件 + 可见文本为空 → 必须有 failure_reason |
| C3 | 无终止事件 + 有可见文本 → 必须有 failure_reason |
| C4 | 必须有 usage，且非负 |
| C5 | 有 first_token_s → 必须声明 first_token_definition |
| C6 | failure_reason=max_tokens → finish_reason 必须可区分 |

## 引用

- 背景报告：https://doi.org/10.5281/zenodo.24269158
- 证据包：https://github.com/yin-kang83/streaming-early-stop-demo/tree/main/evidence/api-compatibility
- Issue #1781：https://github.com/deepseek-ai/DeepSeek-V3/issues/1781
