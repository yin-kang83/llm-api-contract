# -*- coding: utf-8 -*-
"""把 streaming-early-stop-demo 的脱敏证据记录映射为契约记录。"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_api_contract import summarize

SRC = Path(os.environ.get("EVIDENCE_RECORDS", "evidence/api-compatibility/api_protocol_records.sanitized.jsonl"))


def normalize(r):
    terminal = bool(r.get("stream_terminator"))
    text_chars = int(r.get("text_chars") or 0)
    if r.get("error_class") == "EMPTY_TEXT":
        reason = "empty_text"
    elif r.get("error_class") == "STREAM_INCOMPLETE":
        reason = "stream_incomplete"
    elif r.get("finish_reason") == "max_tokens":
        reason = "max_tokens"
    else:
        reason = ""
    return {
        "call_id": f"{r.get('protocol')}:{r.get('dataset')}:{r.get('problem_id')}",
        "provider": "deepseek",
        "protocol": r.get("protocol"),
        "dataset": r.get("dataset"),
        "problem_id": r.get("problem_id"),
        "http_status": 200,
        "terminal_event": terminal,
        "terminal_event_type": "stream_terminator" if terminal else "",
        "visible_text_chars": text_chars,
        "failure_reason": reason,
        "usage": r.get("usage"),
        "finish_reason": r.get("finish_reason") or "",
        "first_token_s": r.get("first_token_s"),
        "first_token_definition": "visible_text" if r.get("first_token_s") is not None else None,
        "stream_event_count": r.get("stream_events"),
        "latency_s": r.get("latency_s"),
    }


def main():
    records = [normalize(json.loads(x)) for x in SRC.read_text(encoding="utf-8").splitlines() if x.strip()]
    s = summarize(records)
    print(json.dumps(s, ensure_ascii=False, indent=2))
    for r in records:
        if not r["terminal_event"] or r["visible_text_chars"] == 0:
            print(f"{r['protocol']}\t{r['problem_id']}\tterminal={r['terminal_event']}\ttext={r['visible_text_chars']}\treason={r['failure_reason']}")


if __name__ == "__main__":
    main()
