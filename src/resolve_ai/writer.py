"""Fixed-structure ANSWER.md / REASONING.md writers plus a machine-readable trace."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from resolve_ai.models import CaseResult


def _bullets(items: List[str], empty: str = "None") -> str:
    return "\n".join(f"- {i}" for i in items) if items else f"- {empty}"


def _status_line(r: CaseResult) -> str:
    last = next((e for e in reversed(r.tool_events) if e.name == "update_case_status" and e.ok), None)
    if last:
        st = str(last.input.get("status", "")).replace("_", " ")
        cm = last.input.get("comment", "")
        return f"**Case status now:** {st}" + (f" — {cm}" if cm else "") + "  "
    if r.resolution.escalation.required:
        return f"**Case status now:** escalated to {r.resolution.escalation.to or 'a human'}  "
    return f"**Case status now:** {r.resolution.decision.replace('_', ' ')}  "


def answer_md(r: CaseResult) -> str:
    x = r.resolution
    esc = x.escalation
    lines = [
        f"# Case {r.case_id} — Answer",
        "",
        _status_line(r),
        f"**Decision:** `{x.decision}`  ",
        f"**Urgency:** `{x.urgency}`  ",
        f"**Issue category:** {x.issue_category}  ",
        f"**Confidence:** {x.confidence:.2f}  ",
        f"**Processing status:** {r.status}" + (f" ({r.error})" if r.error else ""),
        "",
        "## Next action (event n+1)",
        f"**{x.next_action.channel.replace('_', ' ')} → {x.next_action.to}** — {x.next_action.summary}",
        "",
        *([ "> " + line for line in x.next_action.draft.strip().splitlines()] + [""] if x.next_action.draft.strip() else []),
        f"Performed in this run: {'yes' if x.next_action.performed else 'no (recommended)'}",
        *([f"Follow up on **{x.next_action.follow_up_on}**: {x.next_action.follow_up_action or 'check the case again'}"] if x.next_action.follow_up_on else []),
        "",
        *(["Other defensible next actions:", _bullets(x.alternative_next_actions), ""] if x.alternative_next_actions else []),
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


# Assumed human handling time per case when an agent does the legwork (minutes). Stated in INDEX.md as an assumption.
HUMAN_MINUTES_FULL_CASE = 25
HUMAN_MINUTES_ESCALATED_WITH_HANDOVER = 10


def run_summary(results: List[CaseResult]) -> str:
    from collections import Counter
    n = len(results)
    if not n:
        return "No cases.\n"
    done = sum(1 for r in results if r.status == "completed")
    dec = Counter(r.resolution.decision for r in results)
    urg = Counter(r.resolution.urgency for r in results)
    esc = sum(1 for r in results if r.resolution.escalation.required)
    tool_calls = sum(len(r.tool_events) for r in results)
    tool_fail = sum(1 for r in results for e in r.tool_events if not e.ok)
    recovered = sum(1 for r in results if any(not e.ok for e in r.tool_events) and r.status == "completed"
                    and r.resolution.decision in {"resolved", "in_progress", "needs_information", "no_action"})
    gaps = sum(1 for r in results if r.resolution.information_gaps)
    conflicts = sum(1 for r in results if r.resolution.conflicts)
    tokens_in = sum((r.usage or {}).get("input_tokens", 0) for r in results)
    tokens_out = sum((r.usage or {}).get("output_tokens", 0) for r in results)
    minutes = sum(HUMAN_MINUTES_ESCALATED_WITH_HANDOVER if r.resolution.escalation.required else HUMAN_MINUTES_FULL_CASE
                  for r in results if r.status == "completed")
    lines = [
        "## Run summary",
        "",
        f"- Cases: {n}; answered by the agent: {done}; fallback answers (crash/timeout): {n - done}",
        "- Next actions: " + ", ".join(f"{k} {v}" for k, v in Counter(f"{r.resolution.next_action.channel}→{r.resolution.next_action.to}" for r in results).most_common()),
        "- Decisions: " + ", ".join(f"{k} {v}" for k, v in dec.most_common()),
        "- Urgency: " + ", ".join(f"{k} {v}" for k, v in urg.most_common()),
        f"- Escalated to a human: {esc} of {n} ({100 * esc / n:.0f}%), each with a written handover",
        f"- Cases where the agent recorded conflicting information: {conflicts}; where it recorded information gaps: {gaps}",
        f"- Tool calls: {tool_calls}; tool failures: {tool_fail}; cases that completed despite a tool failure: {recovered}",
        f"- Tokens: {tokens_in:,} in / {tokens_out:,} out" if tokens_in or tokens_out else "- Tokens: n/a (mock provider)",
        f"- Estimated human time saved: about {minutes} minutes, assuming {HUMAN_MINUTES_FULL_CASE} min per case handled end to end "
        f"and {HUMAN_MINUTES_ESCALATED_WITH_HANDOVER} min saved on an escalation that arrives with a complete handover. "
        "These are stated assumptions, not measurements.",
        "",
    ]
    return "\n".join(lines)


def write_index(results: List[CaseResult], answers_dir: Path) -> None:
    rows = ["| Case | Status | Next action | Decision | Urgency | Escalated | Confidence |", "|---|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: r.case_id):
        x = r.resolution
        na = f"{x.next_action.channel} → {x.next_action.to}"
        rows.append(f"| [{r.case_id}]({r.case_id}/ANSWER.md) | {r.status} | {na} | {x.decision} | {x.urgency} | {'yes' if x.escalation.required else 'no'} | {x.confidence:.2f} |")
    (answers_dir / "INDEX.md").write_text("# Answers index\n\n" + run_summary(results) + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
