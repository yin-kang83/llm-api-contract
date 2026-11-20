# -*- coding: utf-8 -*-
"""报告生成：按协议/任务形状汇总。"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .checker import check_record, summarize


def build_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_protocol = Counter(r.get("protocol") for r in records)
    by_dataset = Counter(r.get("dataset") for r in records)
    empty = sum(1 for r in records if int(r.get("visible_text_chars") or 0) == 0)
    no_terminal = sum(1 for r in records if not r.get("terminal_event"))
    return {
        "summary": summarize(records),
        "by_protocol": dict(by_protocol),
        "by_dataset": dict(by_dataset),
        "empty_visible_text": empty,
        "no_terminal_event": no_terminal,
        "violations": [
            {"call_id": r.get("call_id"), "violations": check_record(r)}
            for r in records if check_record(r)
        ],
    }
