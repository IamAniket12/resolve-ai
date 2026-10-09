"""Local, deterministic grader. Not the official judge; a fast signal while iterating.

eval/expectations.json:
{
  "case_id": {
    "acceptable_decisions": ["escalated"],
    "acceptable_urgency": ["emergency"],
    "must_escalate": true,
    "required_tools": ["escalate_to_human"],
    "prohibited_tools": ["schedule_contractor"],
    "answer_must_mention": ["0800 111 999"],
    "answer_must_not_mention": ["booked"],
    "notes": "why"
  }
}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


def _latest_run() -> Optional[Path]:
    runs = sorted((p for p in Path("logs").iterdir() if p.is_dir()), key=lambda p: p.name) if Path("logs").exists() else []
    return runs[-1] if runs else None


def grade_run(expectations_path: Path, run_id: Optional[str] = None, verbose: bool = False) -> int:
    exp = json.loads(expectations_path.read_text())
    run_dir = Path("logs") / run_id if run_id else _latest_run()
    if not run_dir or not run_dir.exists():
        print("no run found under logs/")
        return 1
    print(f"grading run {run_dir.name}\n")
    total = passed = 0
    rows = []
    for cid, e in exp.items():
        trace_path = run_dir / cid / "trace.json"
        if not trace_path.exists():
            rows.append((cid, "MISSING", ["no trace.json"]))
            total += 1
            continue
        t = json.loads(trace_path.read_text())
        res = t["resolution"]
        tools_ok = {ev["name"] for ev in t["tool_events"] if ev["ok"]}
        tools_any = {ev["name"] for ev in t["tool_events"]}
        answer_text = json.dumps(res, ensure_ascii=False).lower()
        fails: List[str] = []
        if e.get("acceptable_decisions") and res["decision"] not in e["acceptable_decisions"]:
            fails.append(f"decision {res['decision']} not in {e['acceptable_decisions']}")
        if e.get("acceptable_urgency") and res["urgency"] not in e["acceptable_urgency"]:
            fails.append(f"urgency {res['urgency']} not in {e['acceptable_urgency']}")
        if "must_escalate" in e and bool(res["escalation"]["required"]) != bool(e["must_escalate"]):
            fails.append(f"escalation.required={res['escalation']['required']} expected {e['must_escalate']}")
        for tname in e.get("required_tools", []):
            if tname not in tools_ok:
                fails.append(f"required tool not successfully called: {tname}")
        for tname in e.get("prohibited_tools", []):
            if tname in tools_any:
                fails.append(f"prohibited tool called: {tname}")
        for s in e.get("answer_must_mention", []):
            if s.lower() not in answer_text:
                fails.append(f"answer does not mention '{s}'")
        for s in e.get("answer_must_not_mention", []):
            if s.lower() in answer_text:
                fails.append(f"answer mentions '{s}'")
        if t["status"] != "completed":
            fails.append(f"status={t['status']}")
        total += 1
        if not fails:
            passed += 1
        rows.append((cid, "PASS" if not fails else "FAIL", fails))
    w = max(len(r[0]) for r in rows) if rows else 10
    for cid, status, fails in rows:
        print(f"{cid:{w}s}  {status}")
        if fails and (verbose or status != "PASS"):
            for f in fails:
                print(f"{'':{w}s}    - {f}")
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 2
