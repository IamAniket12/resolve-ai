"""Command-line entry points.

  python -m resolve_ai run     --cases data/sample_cases --out ANSWERS
  python -m resolve_ai inspect --cases data/sample_cases
  python -m resolve_ai grade   --expectations eval/expectations.json [--run <run_id>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from resolve_ai.config import Settings


def cmd_run(args) -> int:
    from resolve_ai.runner import run_cases
    settings = Settings()
    if args.provider:
        settings.llm_provider = args.provider
    if args.tools:
        settings.tool_backend = args.tools
    if args.model:
        settings.model = args.model
    if args.effort:
        settings.effort = args.effort
    results = run_cases(args.cases, args.out, settings, workers=args.workers, case_timeout=args.timeout,
                        only=args.only, run_id=args.run_id)
    bad = [r for r in results if r.status != "completed"]
    return 0 if not bad else 2


def cmd_inspect(args) -> int:
    from resolve_ai.ingest import discover_cases
    from resolve_ai.tools.voice import make_transcriber
    bundles = discover_cases(args.cases, transcriber=make_transcriber(Settings()) if args.transcribe else None)
    print(f"{len(bundles)} cases in {args.cases}\n")
    for b in bundles:
        print(f"== {b.case_id}  ({b.source})")
        for a in b.attachments:
            flag = f"  [{a.note}]" if a.note else ""
            print(f"   - {a.name:40s} {a.kind:10s} {len(a.text):7d} chars{flag}")
        if args.show:
            print(b.text_for_prompt()[: args.show])
            print()
    return 0


def cmd_grade(args) -> int:
    from resolve_ai.grade import grade_run
    return grade_run(Path(args.expectations), args.run, verbose=args.verbose)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="resolve", description="Resolve AI - property maintenance agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="process a folder of cases and write ANSWERS/")
    r.add_argument("--cases", required=True)
    r.add_argument("--out", default="ANSWERS")
    r.add_argument("--workers", type=int)
    r.add_argument("--timeout", type=int, help="seconds per case")
    r.add_argument("--provider", choices=["auto", "anthropic", "mock"])
    r.add_argument("--tools", choices=["mock", "http"])
    r.add_argument("--model")
    r.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    r.add_argument("--only", nargs="*", help="case ids to run")
    r.add_argument("--run-id")
    r.set_defaults(fn=cmd_run)

    i = sub.add_parser("inspect", help="show how cases would be ingested")
    i.add_argument("--cases", required=True)
    i.add_argument("--show", type=int, default=0, help="print first N chars of each prompt")
    i.add_argument("--transcribe", action="store_true")
    i.set_defaults(fn=cmd_inspect)

    g = sub.add_parser("grade", help="score a run against eval/expectations.json")
    g.add_argument("--expectations", default="eval/expectations.json")
    g.add_argument("--run", help="run id under logs/ (default: latest)")
    g.add_argument("-v", "--verbose", action="store_true")
    g.set_defaults(fn=cmd_grade)

    args = p.parse_args(argv)
    sys.exit(args.fn(args))
