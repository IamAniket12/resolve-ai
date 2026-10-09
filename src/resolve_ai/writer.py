"""Fixed-structure ANSWER.md / REASONING.md writers plus a machine-readable trace."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from resolve_ai.models import CaseResult


def _bullets(items: List[str], empty: str = "None") -> str:
    return "\n".join(f"- {i}" for i in items) if items else f"- {empty}"


def answer_md(r: CaseResult) -> str:
    x = r.resolution
    esc = x.escalation
    lines = [
        f"# Case {r.case_id} — Answer",
        "",
        f"**Decision:** `{x.decision}`  ",
        f"**Urgency:** `{x.urgency}`  ",
        f"**Issue category:** {x.issue_category}  ",
        f"**Confidence:** {x.confidence:.2f}  ",
        f"**Processing status:** {r.status}" + (f" ({r.error})" if r.error else ""),
        "",
        "## Summary",
        x.case_summary,
        "",
        "## Outcome",
        x.outcome,
        "",
        "## Actions taken",
        _bullets(x.actions_taken, "No actions were taken"),
        "",
        "## Failed actions and recovery",
        _bullets(x.failed_actions),
        "",
        "## Escalation",
        f"- Required: **{'yes' if esc.required else 'no'}**",
    ]
    if esc.required:
        lines += [f"- To: {esc.to}", f"- Reason: {esc.reason}", "", "### Handover for the human", esc.handover]
    lines += [
        "",
        "## Conflicts in the information",
        _bullets([f"{c.description} — *{c.how_resolved}*" for c in x.conflicts], "No conflicting information found"),
        "",
        "## Information gaps",
        _bullets(x.information_gaps),
        "",
        "## Assumptions",
        _bullets(x.assumptions),
        "",
        "## Communication",
        f"- Tenant: {x.tenant_communication}",
        f"- Landlord: {x.landlord_communication}",
        "",
        "## Risk flags",
        _bullets(x.risk_flags),
        "",
        "## Next steps",
        _bullets(x.next_steps),
        "",
    ]
    return "\n".join(lines)


def reasoning_md(r: CaseResult) -> str:
    x = r.resolution
    lines = [
        f"# Case {r.case_id} — Reasoning and trace",
        "",
        "## What the system received",
        _bullets([f"{m['name']} ({m['kind']}, {m['chars']} chars){' — ' + m['note'] if m.get('note') else ''}" for m in r.manifest], "no files"),
        "",
        "## How the decision was reached",
        x.reasoning,
        "",
        "## Timeline of actions",
    ]
    if not r.tool_events:
        lines.append("- No tool calls were made.")
    for i, e in enumerate(r.tool_events, 1):
        status = "OK" if e.ok else "FAILED"
        out = json.dumps(e.output, ensure_ascii=False, default=str) if e.ok else e.error
        if out and len(out) > 1200:
            out = out[:1200] + " …"
        lines += [f"### {i}. `{e.name}` — {status} (step {e.step}, {e.duration_ms} ms)",
                  "Input:", "```json", json.dumps(e.input, ensure_ascii=False, indent=2)[:1500], "```",
                  "Result:", "```", str(out), "```", ""]
    if r.model_notes:
        lines += ["## Agent notes during the run", _bullets(r.model_notes), ""]
    lines += [
        "## Run metadata",
        f"- Provider/model: {r.provider} / {r.model}",
        f"- Steps: {r.steps}",
        f"- Started: {r.started_at}  Finished: {r.finished_at}",
        f"- Status: {r.status}" + (f" — error: {r.error}" if r.error else ""),
        f"- Token usage: {json.dumps(r.usage)}" if r.usage else "- Token usage: n/a",
        "",
    ]
    return "\n".join(lines)


def write_case(r: CaseResult, answers_dir: Path, log_dir: Path) -> None:
    out = answers_dir / r.case_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "ANSWER.md").write_text(answer_md(r), encoding="utf-8")
    (out / "REASONING.md").write_text(reasoning_md(r), encoding="utf-8")
    case_log = log_dir / r.case_id
    case_log.mkdir(parents=True, exist_ok=True)
    trace = {
        "case_id": r.case_id, "status": r.status, "error": r.error, "provider": r.provider, "model": r.model,
        "steps": r.steps, "started_at": r.started_at, "finished_at": r.finished_at, "usage": r.usage,
        "manifest": r.manifest, "resolution": r.resolution.model_dump(),
        "tool_events": [asdict(e) for e in r.tool_events], "model_notes": r.model_notes,
    }
    (case_log / "trace.json").write_text(json.dumps(trace, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def write_index(results: List[CaseResult], answers_dir: Path) -> None:
    rows = ["| Case | Status | Decision | Urgency | Escalated | Confidence |", "|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: r.case_id):
        x = r.resolution
        rows.append(f"| [{r.case_id}]({r.case_id}/ANSWER.md) | {r.status} | {x.decision} | {x.urgency} | {'yes' if x.escalation.required else 'no'} | {x.confidence:.2f} |")
    (answers_dir / "INDEX.md").write_text("# Answers index\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
