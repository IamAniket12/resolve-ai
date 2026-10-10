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


def cmd_preflight(args) -> int:
    """Everything to check before the Reality Test run, in one command. Spends at most a few tokens."""
    import math
    import time
    from resolve_ai.ingest import discover_cases
    from resolve_ai.tools.registry import ToolRegistry, build_backend
    from resolve_ai.tools.voice import make_transcriber

    settings = Settings()
    if args.provider:
        settings.llm_provider = args.provider
    ok = True
    print(f"== Preflight for {args.cases}\n")

    # 1. cases
    try:
        t0 = time.time()
        bundles = discover_cases(args.cases, transcriber=make_transcriber(settings))
        print(f"[ok] discovered {len(bundles)} cases in {time.time() - t0:.1f}s")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] discovery: {e}")
        return 1
    if not bundles:
        print("[FAIL] no cases found")
        return 1
    sizes = [len(b.text_for_prompt()) for b in bundles]
    unreadable = [(b.case_id, a.name, a.note) for b in bundles for a in b.attachments if a.note and ("could not" in a.note or "failed" in a.note or "binary" in a.note)]
    empty = [b.case_id for b in bundles if not any((a.text or "").strip() for a in b.attachments)]
    print(f"[ok] prompt size per case: min {min(sizes):,} / median {sorted(sizes)[len(sizes)//2]:,} / max {max(sizes):,} chars (~{max(sizes)//4:,} tokens max)")
    if unreadable:
        ok = False
        print(f"[WARN] {len(unreadable)} attachments not readable (the agent is told, but check them):")
        for cid, name, note in unreadable[:10]:
            print(f"       {cid}: {name}: {note}")
    if empty:
        ok = False
        print(f"[WARN] cases with no readable text at all: {empty}")
    dup = {c for c in [b.case_id for b in bundles] if [b.case_id for b in bundles].count(c) > 1}
    if dup:
        ok = False
        print(f"[FAIL] duplicate case ids: {sorted(dup)}")

    # 2. tools backend
    try:
        reg = ToolRegistry(build_backend(settings, "preflight"))
        reg.call("lookup_property", {"query": "preflight"})
        print(f"[ok] tool backend '{settings.tool_backend}' answers")
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] tool backend '{settings.tool_backend}' error on a lookup: {e}")

    # 3. model
    provider = settings.resolved_provider()
    per_case_s = 20.0
    if provider == "anthropic":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=60, max_retries=1)
            t0 = time.time()
            client.messages.create(model=settings.model, max_tokens=5, messages=[{"role": "user", "content": "Reply with OK"}])
            print(f"[ok] Anthropic API reachable, model {settings.model} answered in {time.time() - t0:.1f}s")
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"[FAIL] Anthropic API: {type(e).__name__}: {str(e)[:200]}")
        per_case_s = _avg_case_seconds_from_logs(default=150.0)
        print(f"[info] assumed time per case on the real model: {per_case_s:.0f}s (from recent logs, else default)")
    else:
        print(f"[WARN] provider resolves to '{provider}' (no ANTHROPIC_API_KEY?) - the run would use the mock LLM")

    # 4. plan
    budget = args.minutes * 60
    n = len(bundles)
    workers = max(2, min(args.max_workers, math.ceil(n * per_case_s / (budget * 0.7))))
    timeout = int(min(settings.case_timeout, max(240, budget * 0.6)))
    waves = math.ceil(n / workers)
    print(f"\n[plan] {n} cases, {workers} workers -> ~{waves} waves x {per_case_s:.0f}s ~= {waves * per_case_s / 60:.1f} min of a {args.minutes} min budget; per-case timeout {timeout}s")
    print(f"[plan] command:\n       python -m resolve_ai run --cases \"{args.cases}\" --out ANSWERS --workers {workers} --timeout {timeout}")
    print("\n" + ("PREFLIGHT OK" if ok else "PREFLIGHT HAS WARNINGS - read them before running"))
    return 0 if ok else 2


def _avg_case_seconds_from_logs(default: float) -> float:
    """Average completed-case duration from the most recent anthropic runs under logs/."""
    from datetime import datetime
    logs = Path("logs")
    if not logs.exists():
        return default
    durations = []
    for run in sorted((p for p in logs.iterdir() if p.is_dir()), key=lambda p: p.name, reverse=True)[:5]:
        for tr in run.glob("*/trace.json"):
            try:
                t = json.loads(tr.read_text())
                if t.get("provider") != "anthropic" or t.get("status") != "completed":
                    continue
                a, b = datetime.fromisoformat(t["started_at"]), datetime.fromisoformat(t["finished_at"])
                durations.append((b - a).total_seconds())
            except Exception:  # noqa: BLE001
                continue
    return sum(durations) / len(durations) if durations else default


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

    pf = sub.add_parser("preflight", help="check cases, tools, API and pick workers/timeout before the real run")
    pf.add_argument("--cases", required=True)
    pf.add_argument("--minutes", type=int, default=20, help="wall-clock budget for the whole run")
    pf.add_argument("--max-workers", type=int, default=8)
    pf.add_argument("--provider", choices=["auto", "anthropic", "mock"])
    pf.set_defaults(fn=cmd_preflight)

    g = sub.add_parser("grade", help="score a run against eval/expectations.json")
    g.add_argument("--expectations", default="eval/expectations.json")
    g.add_argument("--run", help="run id under logs/ (default: latest)")
    g.add_argument("-v", "--verbose", action="store_true")
    g.set_defaults(fn=cmd_grade)

    args = p.parse_args(argv)
    sys.exit(args.fn(args))
