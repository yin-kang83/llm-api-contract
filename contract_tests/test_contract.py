# -*- coding: utf-8 -*-
"""5 条离线契约测试（合成记录，不调用 API）。"""
from contract_tests.checker import check_record, summarize


def base(**kw):
    r = {
        "call_id": "c1",
        "provider": "deepseek",
        "protocol": "chat",
        "dataset": "gsm8k",
        "problem_id": "gsm8k:test:1",
        "http_status": 200,
        "terminal_event": True,
        "terminal_event_type": "stop",
        "visible_text_chars": 10,
        "failure_reason": "",
        "usage": {"input": 10, "output": 5},
        "finish_reason": "stop",
        "first_token_s": 0.5,
        "first_token_definition": "visible_text",
        "stream_event_count": 10,
        "latency_s": 1.0,
    }
    r.update(kw)
    return r


def test_complete_stream_passes():
    assert check_record(base()) == []


def test_missing_terminal_and_empty_text_is_flagged():
    r = base(terminal_event=False, terminal_event_type="", visible_text_chars=0)
    codes = [v["code"] for v in check_record(r)]
    assert "C2_EMPTY_NO_REASON" in codes


def test_incomplete_with_text_is_flagged():
    r = base(terminal_event=False, terminal_event_type="", visible_text_chars=138)
    codes = [v["code"] for v in check_record(r)]
    assert "C3_INCOMPLETE_NO_REASON" in codes


def test_usage_missing_is_flagged():
    r = base(usage=None)
    codes = [v["code"] for v in check_record(r)]
    assert "C4_USAGE_MISSING" in codes


def test_first_token_definition_required():
    r = base(first_token_s=3.2, first_token_definition=None)
    codes = [v["code"] for v in check_record(r)]
    assert "C5_FIRST_TOKEN_UNDEFINED" in codes
    r2 = base(first_token_s=3.2, first_token_definition="visible_text")
    assert "C5_FIRST_TOKEN_UNDEFINED" not in [v["code"] for v in check_record(r2)]


def test_summary_counts():
    records = [base(), base(terminal_event=False, visible_text_chars=0)]
    s = summarize(records)
    assert s["total"] == 2
    assert s["violating_records"] == 1
    assert s["clean"] is False
