# -*- coding: utf-8 -*-
"""读取 JSONL 逐调用记录，输出契约违规摘要。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_api_contract import check_record, summarize


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    args = ap.parse_args()
    lines = [x for x in args.path.read_text(encoding="utf-8").splitlines() if x.strip() and not x.lstrip().startswith("#")]
    records = [json.loads(line) for line in lines]
    s = summarize(records)
    print(json.dumps(s, ensure_ascii=False, indent=2))
    for r in records:
        for v in check_record(r):
            print(f"{r.get('call_id')}\t{v['code']}\t{v['message']}")
    return 0 if s["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
