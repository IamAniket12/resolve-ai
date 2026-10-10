"""Data structures shared across ingest, agent, runner and writer."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- inputs ----------

@dataclass
class Attachment:
    name: str
    kind: str  # text | json | csv | email | transcript | pdf | image | audio | unknown
    text: str = ""
    path: Optional[str] = None
    media_type: Optional[str] = None
    note: str = ""  # e.g. "audio transcribed with ElevenLabs" or "could not parse"


@dataclass
class CaseBundle:
    case_id: str
    source: str
    attachments: List[Attachment] = field(default_factory=list)

    def images(self) -> List[Attachment]:
        return [a for a in self.attachments if a.kind == "image" and a.path]

    def manifest(self) -> List[dict]:
        return [
            {"name": a.name, "kind": a.kind, "chars": len(a.text), "note": a.note}
            for a in self.attachments
        ]

    def event_count(self) -> int:
        """Number of history events in the material (the 'n' of the n+1 task), 0 if the format has none."""
        import re
        n = 0
        for a in self.attachments:
            n = max(n, len(re.findall(r'<a id="event-(\d+)"></a>', a.text or "")))
        return n

    def as_of(self) -> str:
        """The case's own 'now': the latest timestamp found in the material (histories are dated, not today)."""
        import re
        pat = re.compile(r"\b(20\d{2}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2})(?::\d{2})?)?")
        best = ""
        for a in self.attachments:
            for m in pat.finditer(a.text or ""):
                stamp = m.group(1) + (" " + m.group(2) if m.group(2) else "")
                if stamp > best:
                    best = stamp
        return best

    def text_for_prompt(self, max_per_attachment: int = 25_000, max_total: int = 180_000) -> str:
        parts: List[str] = []
        total = 0
        for a in self.attachments:
            body = a.text or ""
            if a.kind == "image":
                body = body or "(image attached - see image blocks)"
            if len(body) > max_per_attachment:
                # Keep the head AND the tail: long threads usually carry the real issue near the end.
                head = int(max_per_attachment * 0.6)
                tail = max_per_attachment - head
                cut = len(body) - max_per_attachment
                body = body[:head] + f"\n... [{cut} chars omitted from the middle of this file] ...\n" + body[-tail:]
            block = f"<<<FILE name=\"{a.name}\" kind=\"{a.kind}\"{(' note=' + repr(a.note)) if a.note else ''}>>>\n{body}\n<<<END FILE>>>"
            if total + len(block) > max_total:
                parts.append(f"<<<OMITTED name=\"{a.name}\" reason=\"context budget\">>>")
                continue
            parts.append(block)
            total += len(block)
        return "\n\n".join(parts)


# ---------- agent output (structured) ----------

class Escalation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    required: bool = Field(description="True if a human must decide or act before the case can progress.")
    to: str = Field(default="", description="Who: property manager, landlord, emergency services, compliance, finance, none.")
    reason: str = Field(default="", description="Why a human is needed. Empty if not required.")
    handover: str = Field(default="", description="Everything the human needs to pick this up without re-reading the case: facts, what was done, what is blocked, recommended decision.")


class Conflict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str
    how_resolved: str = Field(description="Which source was trusted and why, or 'unresolved - escalated'.")


class NextAction(BaseModel):
    """The single next action (event n+1) the agency should take now. This is what the case is judged on."""
    model_config = ConfigDict(extra="forbid")
    channel: Literal["email", "sms", "call", "note", "hold", "status_update", "escalate", "book_appointment", "request_approval", "no_action"]
    to: Literal["tenant", "landlord", "contractor", "property_manager", "agency", "none"]
    summary: str = Field(description="One sentence: what the action is and why it is the right next step now.")
    draft: str = Field(default="", description="The message text, hold comment or note exactly as it would be sent or recorded. Empty for no_action.")
    performed: bool = Field(default=False, description="True if this action was carried out via a tool in this run.")
    follow_up_on: str = Field(default="", description="Date (YYYY-MM-DD) when the agency checks this case again if nothing happens, counted from the case date. Required for every hold, chase, approval request or message that expects a reply; empty only for no_action or a closing action.")
    follow_up_action: str = Field(default="", description="What happens on that date if there is still no reply: e.g. 'chase the landlord by email and SMS', 'phone the provider, then re-source', 'escalate to the property manager'.")


class Resolution(BaseModel):
    model_config = ConfigDict(extra="forbid")
    next_action: NextAction = Field(default_factory=lambda: NextAction(channel="no_action", to="none", summary="not set"),
                                    description="The PRIMARY action at event n+1: the one that most matters if only one could happen.")
    next_actions: List[NextAction] = Field(default_factory=list, description="Everything that belongs to the n+1 moment, in order, primary first. Several actions often happen together (e.g. tell the contractor, tell the tenant, set the hold). Do not include steps that depend on a reply.")
    alternative_next_actions: List[str] = Field(default_factory=list, description="Mutually exclusive alternatives to the primary action that a reasonable property manager might choose instead, each in one line, best first, with why it is weaker.")
    case_summary: str = Field(description="2-4 sentences: who reported what, about which property, and what matters.")
    issue_category: str = Field(description="e.g. heating/boiler, plumbing/leak, electrical, gas, damp/mould, pests, appliance, security/locks, structural, not-a-repair, unclear")
    urgency: Literal["emergency", "urgent", "routine", "not_a_repair", "unclear"]
    decision: Literal["resolved", "in_progress", "escalated", "needs_information", "no_action"]
    outcome: str = Field(description="The final state of the case in one or two sentences: what has been arranged or decided.")
    actions_taken: List[str] = Field(description="Concrete actions actually performed via tools, in order. Only actions that succeeded.")
    failed_actions: List[str] = Field(description="Tool calls that failed, with what was tried instead. Empty if none.")
    escalation: Escalation
    conflicts: List[Conflict] = Field(description="Contradictions between sources (tenant vs CRM, history vs message, etc.). Empty if none.")
    information_gaps: List[str] = Field(description="Facts that were missing and how they were handled (asked, assumed, or blocked).")
    assumptions: List[str]
    tenant_communication: str = Field(description="What the tenant has been told, or 'none'.")
    landlord_communication: str = Field(description="What the landlord has been told or asked, or 'none'.")
    next_steps: List[str]
    risk_flags: List[str] = Field(description="Safety, legal, compliance or vulnerability flags. Empty if none.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence that the decision is the right one.")
    reasoning: str = Field(description="Plain-language account of how the decision was reached, including the policy rules applied.")


# ---------- traces ----------

@dataclass
class ToolEvent:
    step: int
    name: str
    input: dict
    output: Any
    ok: bool
    error: Optional[str]
    duration_ms: int


@dataclass
class CaseResult:
    case_id: str
    status: str  # completed | fallback
    resolution: Resolution
    tool_events: List[ToolEvent] = field(default_factory=list)
    model_notes: List[str] = field(default_factory=list)  # visible text the model wrote between tool calls
    started_at: str = ""
    finished_at: str = ""
    provider: str = ""
    model: str = ""
    steps: int = 0
    error: Optional[str] = None
    usage: dict = field(default_factory=dict)
    manifest: List[dict] = field(default_factory=list)


def resolution_schema() -> dict:
    """JSON schema for structured output, tightened for the API's strict subset:
    every property required, no defaults, no numeric bounds, additionalProperties false."""
    import copy

    def tighten(node):
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                node["required"] = list(node["properties"].keys())
                node["additionalProperties"] = False
            for k in ("default", "minimum", "maximum", "title"):
                node.pop(k, None)
            for v in node.values():
                tighten(v)
        elif isinstance(node, list):
            for v in node:
                tighten(v)
        return node

    return tighten(copy.deepcopy(Resolution.model_json_schema()))
