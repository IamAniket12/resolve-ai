"""Local synthetic operating environment. Reads data/mock_env/*.json and keeps
per-case mutable state (tickets, bookings, messages, approvals, escalations, calls).

Failure injection for testing recovery: a contractor record may carry
  "simulate": "unavailable"  -> no slots
  "simulate": "error"        -> availability call raises a transport error
and a tenancy may carry "sms_disabled": true -> SMS to tenant fails.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from resolve_ai.config import Settings
from resolve_ai.tools.registry import ToolError
from resolve_ai.tools import voice


def _load(path: Path) -> List[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


class MockBackend:
    def __init__(self, settings: Settings, case_id: str):
        self.settings = settings
        self.case_id = case_id
        root = Path(settings.mock_env_dir)
        self.properties = _load(root / "properties.json")
        self.tenancies = _load(root / "tenancies.json")
        self.contractors = _load(root / "contractors.json")
        self.history = _load(root / "repair_history.json")
        self.state: Dict[str, List[dict]] = {
            "tickets": [], "bookings": [], "messages": [], "approvals": [],
            "escalations": [], "calls": [], "notes": [],
        }
        self._seq = 0

    # ---------- helpers ----------
    def _ref(self, prefix: str) -> str:
        self._seq += 1
        return f"{prefix}-{uuid.uuid5(uuid.NAMESPACE_DNS, f'{self.case_id}-{prefix}-{self._seq}').hex[:6].upper()}"

    def snapshot(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self.state, default=str))

    def _find_property(self, query: str) -> dict | None:
        q = _norm(query)
        if not q:
            return None
        for p in self.properties:
            if _norm(p["property_id"]) == q:
                return p
        for p in self.properties:
            if q in _norm(p["address"]) or _norm(p["postcode"]) == q:
                return p
        # loose: all tokens of query present in address
        tokens = [t for t in re.split(r"[\s,]+", query.lower()) if len(t) > 2]
        for p in self.properties:
            addr = p["address"].lower() + " " + p["postcode"].lower()
            if tokens and all(t in addr for t in tokens):
                return p
        return None

    def _slots(self, urgency: str, n: int = 3) -> List[dict]:
        """Future slots relative to now: emergency within hours, urgent next working days, routine next 1-2 weeks."""
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        if urgency == "emergency":
            starts = [now + timedelta(hours=2), now + timedelta(hours=5), now + timedelta(hours=22)]
        elif urgency == "urgent":
            d = now.replace(hour=9) + timedelta(days=1)
            starts = [d, d + timedelta(hours=5), d + timedelta(days=1)]
        else:
            d = now.replace(hour=9) + timedelta(days=3)
            starts = [d, d + timedelta(days=3), d + timedelta(days=7)]
        # keep off Sundays for non-emergencies
        if urgency != "emergency":
            starts = [s + timedelta(days=1) if s.weekday() == 6 else s for s in starts]
        return [{"slot_id": f"SLOT-{urgency[:3].upper()}-{i + 1}", "start": s.isoformat(timespec="minutes"),
                 "end": (s + timedelta(hours=2)).isoformat(timespec="minutes")} for i, s in enumerate(starts[:n])]

    # ---------- tools ----------
    def lookup_property(self, query: str) -> dict:
        p = self._find_property(query)
        if not p:
            return {"found": False, "query": query,
                    "note": "No record in the local property database. Treat the case file as the system of record for this "
                            "property: use the address, landlord, tenant and history it contains, and say in the answer that "
                            "the records lookup returned nothing."}
        return {"found": True, **p}

    def lookup_tenancy(self, property_id: str) -> dict:
        ts = [t for t in self.tenancies if _norm(t["property_id"]) == _norm(property_id)]
        if not ts:
            return {"found": False, "property_id": property_id, "tenancies": [], "active_tenancy": None,
                    "note": "No tenancy record in the local database. Use the tenant named in the case file; the platform "
                            "holds their contact details, so messages can be addressed by name or role."}
        active = [t for t in ts if t.get("status") == "active"]
        return {"tenancies": ts, "active_tenancy": active[0] if active else None,
                "warning": None if active else "No ACTIVE tenancy - verify before acting"}

    def get_repair_history(self, property_id: str) -> dict:
        jobs = sorted([j for j in self.history if _norm(j["property_id"]) == _norm(property_id)], key=lambda j: j["date"], reverse=True)
        return {"property_id": property_id, "jobs": jobs, "count": len(jobs)}

    def search_contractors(self, trade: str, postcode: str, emergency: bool) -> dict:
        area = re.match(r"[A-Za-z]+\d*", postcode.strip() or "").group(0).upper() if postcode.strip() else ""
        hits = []
        for c in self.contractors:
            if trade not in c["trades"]:
                continue
            if emergency and not c.get("emergency"):
                continue
            covers = not c.get("postcode_areas") or any(area.startswith(a.upper()) for a in c["postcode_areas"])
            if not covers:
                continue
            hits.append({k: v for k, v in c.items() if k not in {"simulate", "slots"}})
        note = ""
        if not hits:
            # Unknown area (e.g. a postcode outside the panel's coverage): offer the whole panel for the trade.
            hits = [{k: v for k, v in c.items() if k not in {"simulate", "slots"}} for c in self.contractors
                    if trade in c["trades"] and (not emergency or c.get("emergency"))]
            note = ("No contractor covers this postcode area; showing the full panel for the trade. "
                    "Confirm travel/coverage with the contractor before booking." if hits
                    else "No contractors match; try emergency=false, a neighbouring trade, or escalate.")
        hits.sort(key=lambda c: -c.get("rating", 0))
        return {"trade": trade, "postcode": postcode, "emergency_only": emergency, "contractors": hits, "note": note}

    def check_contractor_availability(self, contractor_id: str, urgency: str) -> dict:
        c = next((c for c in self.contractors if c["contractor_id"] == contractor_id), None)
        if not c:
            raise ToolError(f"Unknown contractor {contractor_id}")
        sim = c.get("simulate")
        if sim == "error":
            raise ToolError(f"Contractor scheduling system for {c['name']} returned HTTP 504 (gateway timeout). Retry or choose another contractor.")
        if sim == "unavailable":
            return {"contractor_id": contractor_id, "name": c["name"], "slots": [], "note": "No availability in the next 14 days."}
        slots = c.get("slots", {}).get(urgency) or self._slots(urgency)
        return {"contractor_id": contractor_id, "name": c["name"], "urgency": urgency, "slots": slots}

    def create_maintenance_ticket(self, property_id: str, title: str, category: str, urgency: str, description: str, reported_by: str) -> dict:
        known = self._find_property(property_id)
        t = {"ticket_id": self._ref("TKT"), "property_id": known["property_id"] if known else property_id,
             "property_ref": "records" if known else "case file (not in local database)",
             "title": title, "category": category, "urgency": urgency, "description": description,
             "reported_by": reported_by, "status": "open", "created_at": datetime.now().isoformat(timespec="seconds")}
        self.state["tickets"].append(t)
        return t

    def schedule_contractor(self, ticket_id: str, contractor_id: str, slot_id: str, access_notes: str) -> dict:
        t = next((t for t in self.state["tickets"] if t["ticket_id"] == ticket_id), None)
        if not t:
            raise ToolError(f"Unknown ticket {ticket_id}. Create the ticket first.")
        c = next((c for c in self.contractors if c["contractor_id"] == contractor_id), None)
        if not c:
            raise ToolError(f"Unknown contractor {contractor_id}")
        if c.get("simulate") == "unavailable":
            raise ToolError(f"{c['name']} has no availability; slot {slot_id} cannot be booked.")
        valid_prefix = "SLOT-"
        if not slot_id.startswith(valid_prefix):
            raise ToolError(f"slot_id '{slot_id}' is not a slot returned by check_contractor_availability")
        booking = {"booking_ref": self._ref("BKG"), "ticket_id": ticket_id, "contractor_id": contractor_id,
                   "contractor_name": c["name"], "slot_id": slot_id, "access_notes": access_notes,
                   "status": "confirmed", "estimated_cost_gbp": c.get("call_out_gbp", 95)}
        self.state["bookings"].append(booking)
        t["status"] = "scheduled"
        return booking

    def send_message(self, recipient_type: str, recipient: str, channel: str, body: str) -> dict:
        if not recipient or recipient.lower() in {"unknown", "n/a", "none", ""}:
            raise ToolError("No recipient given. Use a phone number, an email address, or the person's name/role "
                            "(e.g. 'Landlord', 'Felix (landlord)', 'Riverside Works') and the platform will use its contact record.")
        is_phone = bool(re.match(r"^\+?[\d\s()-]{7,}$", recipient))
        is_email = "@" in recipient
        via = "direct" if (is_phone or is_email) else "platform contact record"
        if channel in {"sms", "whatsapp"} and is_email:
            raise ToolError(f"'{recipient}' is an email address; choose channel=email or give a phone number.")
        if channel == "email" and is_phone:
            raise ToolError(f"'{recipient}' is a phone number; choose channel=sms or give an email address.")
        for t in self.tenancies:
            if recipient_type == "tenant" and channel == "sms" and t.get("sms_disabled") and any(recipient.replace(" ", "") == (x.get("phone") or "").replace(" ", "") for x in t["tenants"]):
                raise ToolError("SMS delivery failed: number unreachable (carrier error 30006). Try another channel.")
        m = {"message_id": self._ref("MSG"), "recipient_type": recipient_type, "recipient": recipient, "via": via,
             "channel": channel, "body": body, "status": "delivered", "sent_at": datetime.now().isoformat(timespec="seconds")}
        self.state["messages"].append(m)
        return {"message_id": m["message_id"], "status": "delivered", "via": via}

    def request_landlord_approval(self, ticket_id: str, landlord_id: str, estimated_cost_gbp: float, reason: str) -> dict:
        a = {"approval_id": self._ref("APR"), "ticket_id": ticket_id, "landlord_id": landlord_id,
             "estimated_cost_gbp": estimated_cost_gbp, "reason": reason, "status": "pending",
             "note": "Landlord notified; typical response within 24h. Do not book non-emergency work until approved."}
        self.state["approvals"].append(a)
        return a

    def escalate_to_human(self, ticket_id: str, severity: str, to: str, reason: str, handover: str) -> dict:
        e = {"escalation_id": self._ref("ESC"), "ticket_id": ticket_id, "severity": severity, "to": to,
             "reason": reason, "handover": handover, "status": "queued",
             "created_at": datetime.now().isoformat(timespec="seconds")}
        self.state["escalations"].append(e)
        return {"escalation_id": e["escalation_id"], "status": "queued", "to": to, "severity": severity}

    def place_call(self, to_role: str, phone: str, purpose: str, talking_points: str) -> dict:
        result = voice.place_call(self.settings, to_role=to_role, phone=phone, purpose=purpose, talking_points=talking_points, case_id=self.case_id)
        self.state["calls"].append(result)
        return result

    def update_case_status(self, ticket_id: str, status: str, comment: str) -> dict:
        e = {"status_id": self._ref("STS"), "ticket_id": ticket_id, "status": status, "comment": comment,
             "at": datetime.now().isoformat(timespec="seconds")}
        self.state.setdefault("status_updates", []).append(e)
        return {"status_id": e["status_id"], "status": status, "recorded": True}

    def record_note(self, ticket_id: str, note: str) -> dict:
        n = {"note_id": self._ref("NOTE"), "ticket_id": ticket_id, "note": note}
        self.state["notes"].append(n)
        return {"note_id": n["note_id"], "status": "saved"}
