# 实验 C：event-type traces（2026-11-21）

> 样本：6 个稳定失败 MATH 题 + 2 个对照题；Responses / Anthropic；max_tokens=4000；16 次调用。  
> 只记录事件类型/时间戳，不记录文本。

## 一、最重要的发现：失败不是“没有终止事件”，而是**终止事件没有被识别**

### Responses 失败轨迹

```
response.created
response.in_progress
response.output_item.added
response.content_part.added
response.reasoning_text.delta × 4000
response.reasoning_text.done
response.content_part.done
response.output_item.done
response.incomplete
```

- 失败流有 **4,000 个 reasoning delta**，但 **0 个 output_text delta**；
- 最后事件是 `response.incomplete`，不是“完全没有终止”；
- 当前解析器只把 `response.completed` 当终止，所以把 `response.incomplete` 误归为“无终止/空文本”；
- 这不是纯粹的“协议缺终止事件”，而是 **接线/分类问题**：
  - 服务端发出了 `response.incomplete`；
  - 客户端没识别为终止/失败原因。

### Anthropic 失败轨迹

```
message_start
content_block_start
ping
content_block_delta × 4001
content_block_stop
message_delta
message_stop
```

- `message_stop` 存在，但 `output=4000`、`finish_reason=max_tokens`；
- 4,001 个 delta 全是 thinking 内容，没有 visible text；
- 这是 **thinking 预算耗尽**，不是“流没有结束”。

## 二、成功轨迹对比

| 类型 | reasoning delta | output_text delta | 最终事件 |
|---|---:|---:|---|
| 失败 Responses | 4,000 | 0 | `response.incomplete` |
| 成功 Responses | 2,976–3,362 | 288–696 | `response.completed` |
| 失败 Anthropic | 4,001 thinking delta | 0 | `message_stop`（max_tokens） |
| 成功 Anthropic | 2,109–3,398 delta | 有 visible text | `message_stop`（end_turn） |

## 三、存在两种失败模式

1. **思考预算耗尽型**（主要）
   - Responses：4,000 reasoning delta + `response.incomplete`，usage=0；
   - Anthropic：4,001 thinking delta + `max_tokens`，output=4000；
   - 提高 max_tokens 可能让部分题恢复（A 实验已看到 1/20→4/20、0/20→4/20）。

2. **可见文本后被截断型**（少量）
   - 对照题 3524 Responses：有 696 个 `output_text.delta`（1594 字符），但最后是 `response.incomplete`；
   - 这是真正的流式终止/截断问题，不只是 thinking 预算。

## 四、对之前结论的修正

| 之前说法 | 修正 |
|---|---|
| Responses “没有终止事件” | 不准确：有 `response.incomplete`；是解析器未识别 |
| “空文本就是模型没输出” | 不准确：多数是 thinking 吃满预算，visible text 尚未开始 |
| “协议缺陷” | 一部分是协议/客户端分类问题；一部分是 thinking 预算问题；少量是真截断 |
| “加 token 没用” | 不能这么说：trace 显示 thinking 确实占满预算，8000/16000 值得小样本验证 |

## 五、限制

- 6 个失败 ID 是事后选出的；
- 每个条件只 1 次 trace；
- 无法看到 thinking 文本内容（只记录事件类型）；
- `response.incomplete` 的具体 `reason` 字段未记录（下一步可加，不记录文本）。

## 六、下一步

1. 修正解析器：识别 `response.incomplete` 为终止事件，并记录 stop reason（不记录文本）；
2. 更新 120/240/720 报告中“missing terminal”的表述；
3. 小样本测试 **8000**（6 失败 ID ×2 协议 =12 次），若 8000 明显恢复，再测 16000；
4. 对 3524 类“有 visible text 后 incomplete”单独归类为 stream truncation。
