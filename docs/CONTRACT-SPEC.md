# Per-call record schema (v0.1)

每条调用一条 JSON（JSONL），不含 prompt/raw/output 文本。

| 字段 | 类型 | 说明 |
|---|---|---|
| `call_id` | string | 本地唯一 id（不含用户信息） |
| `provider` | string | `deepseek` / other |
| `protocol` | string | `chat` / `responses` / `anthropic` |
| `model_requested` | string | 请求模型 |
| `model_returned` | string | 响应中的模型名 |
| `dataset` | string | `gsm8k` / `math` / other |
| `problem_id` | string | 公开数据集题号 |
| `timestamp` | string | UTC ISO8601 |
| `http_status` | int | HTTP 层状态 |
| `terminal_event` | bool | 是否收到明确终止事件 |
| `terminal_event_type` | string | `response.completed` / `message_stop` / `[DONE]` / `stop` / empty |
| `visible_text_chars` | int | 可见文本字符数（不含 thinking） |
| `failure_reason` | string | `empty_text` / `stream_incomplete` / `max_tokens` / `timeout` / `http_error` / `""` |
| `usage` | object | `{input, output}`；缺失用 `null` |
| `thinking_tokens` | int/null | 如 provider 提供 |
| `finish_reason` | string | provider 返回的 finish/stop reason |
| `first_token_s` | number/null | 首个可见 token 时间 |
| `first_token_definition` | string | `any_event` / `visible_text` / `null` |
| `stream_event_count` | int | 流事件数 |
| `latency_s` | number | 总延迟 |
| `prompt_sha256` | string | prompt 哈希（不可逆） |
| `answer_sha256` | string | 参考答案哈希（不可逆） |

## 隐私边界

- 不记录 prompt/题面/答案/模型原始输出；
- 不记录 API key、用户 id、IP、本机路径；
- `problem_id` 仅公开数据集 id；
- 所有哈希只用于一致性核对。
