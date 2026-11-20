# -*- coding: utf-8 -*-
"""离线 API 契约检查器（v0.1）。

只检查“记录形态/协议语义”，不调用 API、不读取 prompt/raw。
"""
from __future__ import annotations

from typing import Any


def check_record(r: dict[str, Any]) -> list[dict[str, str]]:
    """返回 violations 列表；空列表=通过。"""
    out: list[dict[str, str]] = []

    def bad(code: str, msg: str) -> None:
        out.append({"code": code, "message": msg})

    # C1: 声明终止事件，必须有类型
    if r.get("terminal_event") is True and not r.get("terminal_event_type"):
        bad("C1_TERMINAL_TYPE_MISSING", "terminal_event=true 但 terminal_event_type 为空")

    # C2/C3: 非正常结束必须有 failure_reason
    text_chars = int(r.get("visible_text_chars") or 0)
    if r.get("terminal_event") is not True:
        if not r.get("failure_reason"):
            if text_chars == 0:
                bad("C2_EMPTY_NO_REASON", "无终止事件且可见文本为空，但无 failure_reason")
            else:
                bad("C3_INCOMPLETE_NO_REASON", "无终止事件但有可见文本，但无 failure_reason")

    # C4: usage 字段必须存在；失败流缺 usage 不可接受
    usage = r.get("usage", "MISSING")
    if usage == "MISSING" or usage is None:
        bad("C4_USAGE_MISSING", "缺少 usage 字段")
    else:
        try:
            if int(usage.get("input", -1)) < 0 or int(usage.get("output", -1)) < 0:
                bad("C4_USAGE_NEGATIVE", "usage 为负值")
        except Exception:
            bad("C4_USAGE_BAD_SHAPE", "usage 不是 {input:int, output:int}")

    # C5: 有 first_token_s 就必须声明定义
    if r.get("first_token_s") is not None:
        d = r.get("first_token_definition")
        if d not in ("any_event", "visible_text"):
            bad("C5_FIRST_TOKEN_UNDEFINED", "first_token_s 存在但 first_token_definition 缺失/非法")

    # 额外：thinking 打满时，finish_reason 应可区分
    if r.get("failure_reason") == "max_tokens" and not r.get("finish_reason"):
        bad("C6_MAX_TOKENS_NO_FINISH_REASON", "failure_reason=max_tokens 但 finish_reason 为空")

    return out


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    flagged = [r for r in records if check_record(r)]
    codes: dict[str, int] = {}
    for r in flagged:
        for v in check_record(r):
            codes[v["code"]] = codes.get(v["code"], 0) + 1
    return {
        "total": total,
        "violating_records": len(flagged),
        "violation_codes": codes,
        "clean": len(flagged) == 0,
    }
