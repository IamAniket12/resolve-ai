"""The case-working loop: understand -> verify -> triage -> act -> recover -> report."""
from __future__ import annotations

import base64
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from resolve_ai.config import Settings
from resolve_ai.llm import LLM
from resolve_ai.models import CaseBundle, CaseResult, Resolution, ToolEvent, resolution_schema
from resolve_ai.prompts import FINALIZE_PROMPT, build_case_prompt, build_system_prompt
from resolve_ai.tools.registry import ToolError, ToolRegistry, to_tool_result_text

log = logging.getLogger(__name__)
MAX_IMAGES = 4
MAX_TOOL_RESULT_CHARS = 30_000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _case_content(bundle: CaseBundle, include_images: bool) -> Any:
    text = build_case_prompt(bundle)
    if not include_images:
        return text
    blocks: List[Dict[str, Any]] = [{"type": "text", "text": text}]
    for img in bundle.images()[:MAX_IMAGES]:
        try:
            data = base64.standard_b64encode(open(img.path, "rb").read()).decode()
            blocks.append({"type": "image", "source": {"type": "base64", "media_type": img.media_type or "image/jpeg", "data": data}})
            blocks.append({"type": "text", "text": f"(above image: {img.name})"})
        except OSError as e:
            blocks.append({"type": "text", "text": f"(image {img.name} could not be read: {e})"})
    return blocks


class ResolveAgent:
    def __init__(self, llm: LLM, settings: Settings, policy: str, registry_factory):
        self.llm = llm
        self.settings = settings
        self.system = build_system_prompt(policy)
        self.registry_factory = registry_factory
        self.schema = resolution_schema()

    def run(self, bundle: CaseBundle, deadline: Optional[float] = None, trace_cb=None, grace: float = 45.0) -> CaseResult:
        started = _now()
        registry: ToolRegistry = self.registry_factory(bundle)
        tools = registry.definitions()
        messages: List[dict] = [{"role": "user", "content": _case_content(bundle, include_images=self.llm.name == "anthropic")}]
        events: List[ToolEvent] = []
        notes: List[str] = []
        seen_calls: Dict[str, int] = {}
        usage: Dict[str, int] = {}
        steps = 0
        stop_note = None

        for step in range(1, self.settings.max_steps + 1):
            if deadline and time.time() > deadline - grace:
                stop_note = "stopped early: case deadline approaching"
                break
            resp = self.llm.step(self.system, messages, tools)
            steps = step
            for k, v in resp.usage.items():
                usage[k] = usage.get(k, 0) + v
            messages.append({"role": "assistant", "content": resp.content})
            for b in resp.content:
                if b.get("type") == "text" and b.get("text", "").strip():
                    notes.append(b["text"].strip())
                    if trace_cb:
                        trace_cb(f"[{bundle.case_id}] model: {b['text'].strip()[:200]}")
            tool_uses = [b for b in resp.content if b.get("type") == "tool_use"]
            if resp.stop_reason == "refusal":
                stop_note = "model refusal"
                break
            if resp.stop_reason == "pause_turn":
                continue
            if not tool_uses:
                break
            results = []
            for tu in tool_uses:
                key = f"{tu.get('name')}:{json.dumps(tu.get('input'), sort_keys=True, default=str)}"
                seen_calls[key] = seen_calls.get(key, 0) + 1
                if seen_calls[key] >= 3:
                    ev = ToolEvent(step, tu.get("name", "?"), tu.get("input") or {}, None, False,
                                   "duplicate call blocked: this exact call already ran; use the earlier result or finish the case", 0)
                else:
                    ev = self._run_tool(registry, step, tu)
                events.append(ev)
                if trace_cb:
                    trace_cb(f"[{bundle.case_id}] tool {ev.name} {'ok' if ev.ok else 'ERROR'} ({ev.duration_ms}ms)")
                content = to_tool_result_text(ev.output if ev.ok else {"error": ev.error})
                if len(content) > MAX_TOOL_RESULT_CHARS:
                    content = content[:MAX_TOOL_RESULT_CHARS] + "... [truncated]"
                results.append({"type": "tool_result", "tool_use_id": tu["id"], "content": content, "is_error": not ev.ok})
            messages.append({"role": "user", "content": results})
        else:
            stop_note = f"stopped: reached max steps ({self.settings.max_steps})"

        if stop_note:
            notes.append(stop_note)

        final_messages = messages + [{"role": "user", "content": FINALIZE_PROMPT + (f"\nNote: {stop_note}." if stop_note else "")}]
        data = self.llm.finalize(self.system, final_messages, tools, self.schema)
        fin_usage = data.pop("_usage", {}) if isinstance(data, dict) else {}
        for k, v in fin_usage.items():
            usage[k] = usage.get(k, 0) + v
        resolution = Resolution.model_validate(data)

        return CaseResult(
            case_id=bundle.case_id, status="completed", resolution=resolution, tool_events=events,
            model_notes=notes, started_at=started, finished_at=_now(), provider=self.llm.name,
            model=self.llm.model, steps=steps, usage=usage, manifest=bundle.manifest(),
        )

    @staticmethod
    def _run_tool(registry: ToolRegistry, step: int, tu: dict) -> ToolEvent:
        name, inp = tu.get("name", "?"), tu.get("input") or {}
        if isinstance(inp, str):
            try:
                inp = json.loads(inp)
            except json.JSONDecodeError:
                return ToolEvent(step, name, {"raw": inp}, None, False, "tool input was not valid JSON", 0)
        t0 = time.time()
        try:
            out = registry.call(name, inp)
            return ToolEvent(step, name, inp, out, True, None, int((time.time() - t0) * 1000))
        except ToolError as e:
            return ToolEvent(step, name, inp, None, False, str(e), int((time.time() - t0) * 1000))
        except Exception as e:  # noqa: BLE001 - a tool bug must not kill the case
            log.exception("tool %s crashed", name)
            return ToolEvent(step, name, inp, None, False, f"internal tool error: {type(e).__name__}: {e}", int((time.time() - t0) * 1000))


def fallback_result(bundle: CaseBundle, error: str, events: Optional[List[ToolEvent]] = None, provider: str = "") -> CaseResult:
    """Written when the agent could not finish. Honest, safe, and still a complete answer."""
    events = events or []
    done = [f"{e.name}({json.dumps(e.input)[:120]})" for e in events if e.ok]
    failed = [f"{e.name}: {e.error}" for e in events if not e.ok]
    res = Resolution(
        next_action={"channel": "escalate", "to": "property_manager", "summary": "Hand the case to a person: the automated run could not complete.", "draft": "", "performed": False},
        case_summary=f"Case {bundle.case_id}: automated processing did not complete ({error[:200]}). Files received: {', '.join(a.name for a in bundle.attachments) or 'none'}.",
        issue_category="unclear", urgency="unclear", decision="escalated",
        outcome="Not resolved autonomously. Escalated to the property manager with the partial trace so no case is dropped.",
        actions_taken=done, failed_actions=failed + [f"agent run aborted: {error[:300]}"],
        escalation={"required": True, "to": "property_manager", "reason": "Automated processing failed before a safe decision could be reached.",
                    "handover": "Review the attached case material and the partial tool trace in REASONING.md. Treat the reported issue as one urgency band higher than it appears until verified."},
        conflicts=[], information_gaps=["Automated analysis incomplete"], assumptions=[],
        tenant_communication="none", landlord_communication="none",
        next_steps=["Property manager to triage manually", "Re-run agent once the underlying failure is fixed"],
        risk_flags=["processing failure - verify manually"], confidence=0.0,
        reasoning="The agent could not complete this case. Rather than guess, it escalates with everything gathered so far.",
    )
    return CaseResult(case_id=bundle.case_id, status="fallback", resolution=res, tool_events=events,
                      started_at=_now(), finished_at=_now(), provider=provider, error=error, manifest=bundle.manifest())
