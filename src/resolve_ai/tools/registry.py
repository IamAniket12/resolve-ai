"""Tool definitions exposed to the model, and the adapter that routes each call to a
backend (mock environment or the event's real APIs). The agent never knows which.

Adding a tool = add a definition here + implement `<name>` on the backends.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from resolve_ai.config import Settings

log = logging.getLogger(__name__)


class ToolError(Exception):
    """A tool failed in a way the model should see (returned as is_error tool_result)."""


def _schema(props: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": props,
        "required": list(props.keys()),
        "additionalProperties": False,
    }


TRADES = ["plumber", "gas_engineer", "electrician", "roofer", "locksmith", "handyperson",
          "pest_control", "appliance_engineer", "damp_specialist", "glazier", "drainage"]
URGENCY = ["emergency", "urgent", "routine"]

TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "lookup_property",
        "description": "Find a property record by property ID, full/partial address, or postcode. Returns the property, landlord details, landlord instructions, spend limit, preferred contractors and compliance dates. Returns an error if nothing matches - never guess a property.",
        "input_schema": _schema({"query": {"type": "string", "description": "Property ID (e.g. PROP-0042), address fragment, or postcode"}}),
    },
    {
        "name": "lookup_tenancy",
        "description": "Get the current tenancy for a property: tenants, contact details, status, vulnerability notes and access notes.",
        "input_schema": _schema({"property_id": {"type": "string"}}),
    },
    {
        "name": "get_repair_history",
        "description": "List previous maintenance jobs for a property (date, category, contractor, cost, outcome). Use it to spot recurring faults and warranty callbacks.",
        "input_schema": _schema({"property_id": {"type": "string"}}),
    },
    {
        "name": "search_contractors",
        "description": "Search the approved contractor panel by trade and area. Returns contractors with certifications, rating, emergency capability and contact details. Only book contractors returned here.",
        "input_schema": _schema({
            "trade": {"type": "string", "enum": TRADES},
            "postcode": {"type": "string", "description": "Property postcode, used to match coverage area"},
            "emergency": {"type": "boolean", "description": "True to restrict to contractors offering emergency call-out"},
        }),
    },
    {
        "name": "check_contractor_availability",
        "description": "Get bookable slots for a contractor for the given urgency band. Returns slot IDs with start/end times. May fail if the contractor's system is down.",
        "input_schema": _schema({
            "contractor_id": {"type": "string"},
            "urgency": {"type": "string", "enum": URGENCY},
        }),
    },
    {
        "name": "create_maintenance_ticket",
        "description": "Open a maintenance ticket against a verified property. Do this before booking a contractor.",
        "input_schema": _schema({
            "property_id": {"type": "string"},
            "title": {"type": "string"},
            "category": {"type": "string", "description": "e.g. heating, plumbing, electrical, gas, damp_mould, pests, appliance, security, structural, other"},
            "urgency": {"type": "string", "enum": URGENCY},
            "description": {"type": "string", "description": "What was reported, by whom, and relevant history"},
            "reported_by": {"type": "string", "description": "Name/role of the reporter"},
        }),
    },
    {
        "name": "schedule_contractor",
        "description": "Book a contractor slot against a ticket. Requires a slot_id returned by check_contractor_availability. Returns a booking reference.",
        "input_schema": _schema({
            "ticket_id": {"type": "string"},
            "contractor_id": {"type": "string"},
            "slot_id": {"type": "string"},
            "access_notes": {"type": "string", "description": "How the contractor gets in; keep personal data minimal"},
        }),
    },
    {
        "name": "send_message",
        "description": "Send a message to the tenant, landlord, contractor or property manager. Give a phone number or email if you have one; otherwise give the person's name or role as it appears in the case file and the platform uses its own contact record for that party. Returns a delivery receipt or an error.",
        "input_schema": _schema({
            "recipient_type": {"type": "string", "enum": ["tenant", "landlord", "contractor", "property_manager"]},
            "recipient": {"type": "string", "description": "Phone number, email address, or the recipient's name/role from the case file (e.g. 'Felix (landlord)', 'Riverside Works')"},
            "channel": {"type": "string", "enum": ["sms", "email", "whatsapp", "portal"]},
            "body": {"type": "string"},
        }),
    },
    {
        "name": "request_landlord_approval",
        "description": "Ask the landlord to approve spend above the pre-authorised limit. Creates a pending approval; the job must not be booked as non-emergency until approved.",
        "input_schema": _schema({
            "ticket_id": {"type": "string"},
            "landlord_id": {"type": "string"},
            "estimated_cost_gbp": {"type": "number"},
            "reason": {"type": "string"},
        }),
    },
    {
        "name": "escalate_to_human",
        "description": "Hand the case (or a decision within it) to a human. Use for safety rules, decisions above authority, unresolved conflicts, repeated failures, or anything outside maintenance. The handover must let the human act without re-reading the case.",
        "input_schema": _schema({
            "ticket_id": {"type": "string", "description": "Ticket ID if one exists, else empty string"},
            "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
            "to": {"type": "string", "enum": ["property_manager", "landlord", "compliance", "finance", "emergency_services_advised"]},
            "reason": {"type": "string"},
            "handover": {"type": "string", "description": "Facts, sources, actions taken, what is blocked, recommended decision"},
        }),
    },
    {
        "name": "place_call",
        "description": "Place a voice call (via ElevenLabs conversational agent) to a contractor, tenant or landlord to confirm a booking, obtain access times, or gather a missing fact. Returns the call outcome and a transcript summary. Use when a message is not enough (emergencies, confirmations needed now).",
        "input_schema": _schema({
            "to_role": {"type": "string", "enum": ["tenant", "landlord", "contractor"]},
            "phone": {"type": "string"},
            "purpose": {"type": "string"},
            "talking_points": {"type": "string", "description": "What the voice agent must confirm or ask, as bullet points"},
        }),
    },
    {
        "name": "update_case_status",
        "description": "Set the case's workflow state the way the agency's operations platform does (e.g. put on hold waiting for the landlord, mark provider assigned, mark completed). Use this to record where the case now stands and why.",
        "input_schema": _schema({
            "ticket_id": {"type": "string", "description": "Ticket ID or empty string"},
            "status": {"type": "string", "enum": ["awaiting_landlord", "awaiting_tenant", "awaiting_provider", "awaiting_quote",
                                                   "provider_assigned", "appointment_booked", "awaiting_invoice", "completed",
                                                   "completed_without_payment", "closed_no_action", "escalated"]},
            "comment": {"type": "string", "description": "One line a colleague would read on the dashboard: reason and next check date"},
        }),
    },
    {
        "name": "record_note",
        "description": "Add an internal note to the ticket (observations, conflicts noticed, assumptions). Not visible to tenant or landlord.",
        "input_schema": _schema({
            "ticket_id": {"type": "string", "description": "Ticket ID or empty string"},
            "note": {"type": "string"},
        }),
    },
]

READ_ONLY_TOOLS = {"lookup_property", "lookup_tenancy", "get_repair_history", "search_contractors",
                   "check_contractor_availability", "record_note", "update_case_status"}


class ToolRegistry:
    """Routes model tool calls to a backend and validates inputs lightly."""

    def __init__(self, backend):
        self.backend = backend
        self._defs = {t["name"]: t for t in TOOL_DEFINITIONS}

    def definitions(self) -> List[Dict[str, Any]]:
        return [{**t, "strict": True} for t in TOOL_DEFINITIONS]

    def call(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._defs:
            raise ToolError(f"unknown tool: {name}")
        required = self._defs[name]["input_schema"]["required"]
        missing = [k for k in required if k not in payload]
        if missing:
            raise ToolError(f"missing required fields for {name}: {missing}")
        handler = getattr(self.backend, name, None)
        if handler is None:
            raise ToolError(f"backend {type(self.backend).__name__} does not implement {name}")
        result = handler(**payload)
        if not isinstance(result, dict):
            result = {"result": result}
        return result

    def state_snapshot(self) -> Dict[str, Any]:
        snap = getattr(self.backend, "snapshot", None)
        return snap() if snap else {}


def build_backend(settings: Settings, case_id: str):
    """Pick the backend. `http` routes the tools listed in HTTP_TOOLS (or all with '*')
    to the event API and everything else to the mock, so we can mix during the day."""
    from resolve_ai.tools.mock_backend import MockBackend
    mock = MockBackend(settings, case_id)
    if settings.tool_backend == "mock":
        return mock
    from resolve_ai.tools.http_backend import CompositeBackend, HttpBackend
    http = HttpBackend(settings)
    return CompositeBackend(http=http, mock=mock, http_tools=settings.http_tools)


def to_tool_result_text(result: Any) -> str:
    try:
        return json.dumps(result, ensure_ascii=False, default=str)
    except TypeError:
        return str(result)
