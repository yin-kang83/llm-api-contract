# API Contract Pre-Registration (v0.1)

> 研究线：LLM API 协议语义与评测测量效度  
> 状态：预注册草案；本文件先冻结“看什么、怎么算、什么算异常”，再扩样。

## 1. 研究问题

1. 同一 prompt/参数下，不同协议（chat / responses / anthropic-compatible）的**终止事件**是否一致、可判定？
2. 失败的流式调用是否携带**可判定的失败原因**与 **usage**？
3. `usage`、`first_token`、`thinking budget` 的字段语义是否跨协议可比？
4. 上述差异是否与**任务形状**（题型/难度）相关？
5. 在“确定矛盾”条件下早停，是否能降低 token/延迟且不误停？

## 2. 范围（v0.1）

- 模型/provider：DeepSeek 官方 API 的 chat、Responses、Anthropic-compatible 三协议；
- 数据集：GSM8K 20 题 + MATH 20 题（固定 seed / 题号清单）；
- 每协议 40 次调用，单次、无重试；
- 参数：temperature=0、max_tokens=2000、stream=true；
- 记录：每调用一条 JSON（字段见 `CONTRACT-SPEC.md`）。

**不做**：模型能力排名、跨协议性能结论、对未公开模型的行为推断。

## 3. 指标（预注册）

| 指标 | 定义 |
|---|---|
| `terminal_event_rate` | 收到明确终止事件的调用数 / 总调用数 |
| `empty_visible_text_rate` | 可见文本为空的比例 |
| `failure_reason_rate` | 失败调用中带可判定 reason 的比例 |
| `usage_missing_rate` | 无 usage 或 usage 为 0 的失败调用比例 |
| `first_token_defined_rate` | 记录了 `first_token_definition` 的调用比例 |
| `task_cluster` | 失败按 dataset/problem 类型的分布 |

## 4. 判定规则（contract tests）

- C1：声明 `terminal_event=true` 的调用，必须存在终止事件类型；
- C2：可见文本为空且 `terminal_event=false` 的调用，必须带 `failure_reason`；
- C3：`terminal_event=false` 且可见文本非空，也必须有 `failure_reason`（如 incomplete/truncated）；
- C4：任何调用都必须有 `usage` 字段；失败流若无 usage，记为 contract violation；
- C5：`first_token_s` 必须带 `first_token_definition ∈ {any_event, visible_text}`，否则不可比。

## 5. 停止规则与排除

- 单协议连续 5 次 HTTP/连接错误 → 停止该协议，记录为 infra failure；
- 响应文本/流事件缺失但 HTTP 200 → 记为 observation，不重试；
- 超时 60s → 记录 timeout，不重试；
- 排除：鉴权失败、配额失败（记为 infra，不进入协议统计）。

## 6. 产出

1. `docs/API-CONTRACT-PREREG.md`（本文件）；
2. `CONTRACT-SPEC.md`（记录字段定义）；
3. `contract_tests/`（五条纯离线检查 + pytest）；
4. 脱敏逐调用记录（JSONL，无 prompt/raw）；
5. 报告 v0.2：失败率、原因分布、任务聚类、usage/first-token 口径问题；
6. 有实质发现再回 Issue #1781。

## 7. 限制

- 单模型、单次运行、小样本；
- provider 版本/别名会变，需记录时间戳与返回模型名；
- 不宣称“已修复/已标准化”；
- 不构成模型能力评测。
