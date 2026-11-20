# -*- coding: utf-8 -*-
"""记录 schema 校验（v0.1）。"""
from __future__ import annotations

from typing import Any

REQUIRED = [
    "call_id", "provider", "protocol", "dataset", "problem_id",
    "terminal_event", "terminal_event_type", "visible_text_chars",
    "failure_reason", "usage", "first_token_s", "first_token_definition",
    "stream_event_count", "latency_s",
]

PROTOCOLS = {"chat", "responses", "anthropic"}
FIRST_TOKEN_DEFS = {"any_event", "visible_text", None}


def validate_record(r: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for k in REQUIRED:
        if k not in r:
            errors.append(f"missing field: {k}")
    if r.get("protocol") not in PROTOCOLS:
        errors.append("protocol 必须是 chat/responses/anthropic")
    if r.get("first_token_definition") not in FIRST_TOKEN_DEFS:
        errors.append("first_token_definition 必须是 any_event/visible_text/null")
    if not isinstance(r.get("visible_text_chars"), (int, float)) or int(r.get("visible_text_chars", -1)) < 0:
        errors.append("visible_text_chars 必须是非负整数")
    u = r.get("usage")
    if u is not None:
        if not isinstance(u, dict) or "input" not in u or "output" not in u:
            errors.append("usage 必须是 {input, output} 或 null")
    return errors
