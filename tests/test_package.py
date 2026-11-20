# -*- coding: utf-8 -*-
from llm_api_contract import build_report, check_record, summarize


def test_package_import_and_check():
    r = {
        "call_id": "c1",
        "provider": "deepseek",
        "protocol": "chat",
        "dataset": "gsm8k",
        "problem_id": "gsm8k:test:1",
        "terminal_event": True,
        "terminal_event_type": "stop",
        "visible_text_chars": 10,
        "failure_reason": "",
        "usage": {"input": 10, "output": 5},
        "first_token_s": 0.5,
        "first_token_definition": "visible_text",
        "stream_event_count": 10,
        "latency_s": 1.0,
    }
    assert check_record(r) == []
    assert summarize([r])["clean"] is True
    assert build_report([r])["summary"]["total"] == 1
