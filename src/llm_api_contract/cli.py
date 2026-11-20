# -*- coding: utf-8 -*-
"""CLI：check / report。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .checker import check_record, summarize
from .report import build_report


def _load(path: Path) -> list[dict]:
    lines = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip() and not x.lstrip().startswith("#")]
    return [json.loads(x) for x in lines]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="llm-api-contract")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("check")
    p1.add_argument("path", type=Path)
    p1.add_argument("--json", type=Path, default=None)

    p2 = sub.add_parser("report")
    p2.add_argument("path", type=Path)
    p2.add_argument("--json", type=Path, default=None)

    args = ap.parse_args(argv)
    records = _load(args.path)

    if args.cmd == "check":
        s = summarize(records)
        print(json.dumps(s, ensure_ascii=False, indent=2))
        for r in records:
            for v in check_record(r):
                print(f"{r.get('call_id')}\t{v['code']}\t{v['message']}")
        if args.json:
            args.json.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if s["clean"] else 1

    report = build_report(records)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
