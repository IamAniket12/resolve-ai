"""Deterministic stand-in for Claude so the whole pipeline (ingest -> tools -> answers)
can be exercised with no API key. It follows the policy with keyword rules. It is NOT
the product; it exists to test plumbing, the runner and the writers.
"""
from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Optional

from resolve_ai.config import Settings
from resolve_ai.llm import LLM, LLMResponse

GAS_WORDS = ["smell of gas", "gas smell", "smell gas", "carbon monoxide", "co alarm", "gas leak"]
ELEC_WORDS = ["sparking", "sparks ", "is sparking", "burning smell", "electric shock", "exposed wire", "sockets wet", "water in the light", "ceiling light fitting", "through the light", "fuse box smoking"]
INJECTION_WORDS = ["system note to ai", "note to ai assistant", "ignore your", "skip the approval", "ignore previous", "you are now"]
LEAK_WORDS = ["leak", "water coming", "dripping", "flood", "ceiling", "burst"]
HEAT_WORDS = ["boiler", "no heating", "no hot water", "heating", "radiator"]
MOULD_WORDS = ["mould", "mold", "damp", "condensation"]
LOCK_WORDS = ["lock", "break-in", "broken window", "can't secure", "door won't"]
APPLIANCE_WORDS = ["washing machine", "dishwasher", "tumble dryer", "fridge", "freezer", "oven", "cooker", "hob"]
TENANT_DAMAGE_WORDS = ["i dropped", "my fault", "that's on me", "i broke", "accidentally", "i'll cover it", "own up"]
AMBIGUITY_WORDS = ["didn't check", "haven't checked", "not sure if", "could be either"]
VULN_WORDS = ["baby", "infant", "elderly", "disabled", "pregnan", "oxygen", "newborn", "months old", "wheelchair", "dialysis"]


def _tool_use(name: str, inp: dict) -> dict:
    return {"type": "tool_use", "id": f"toolu_{uuid.uuid4().hex[:12]}", "name": name, "input": inp}


def _text(t: str) -> dict:
    return {"type": "text", "text": t}


class MockLLM(LLM):
    name = "mock"
    model = "mock-rules-v1"

    def __init__(self, settings: Settings):
        self.settings = settings

    # ----- helpers to read the conversation -----
    @staticmethod
    def _case_text(messages: List[dict]) -> str:
        first = messages[0]["content"]
        if isinstance(first, str):
            return first
        return "\n".join(b.get("text", "") for b in first if isinstance(b, dict) and b.get("type") == "text")

    @staticmethod
    def _results(messages: List[dict]) -> Dict[str, List[dict]]:
        """Map tool name -> list of parsed results (dict with ok flag)."""
        calls: Dict[str, dict] = {}
        out: Dict[str, List[dict]] = {}
        for m in messages:
            if m["role"] == "assistant":
                for b in m["content"]:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        calls[b["id"]] = b
            elif isinstance(m["content"], list):
                for b in m["content"]:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        call = calls.get(b["tool_use_id"], {})
                        raw = b.get("content")
                        text = raw if isinstance(raw, str) else "".join(x.get("text", "") for x in raw or [])
                        try:
                            data = json.loads(text)
                        except (json.JSONDecodeError, TypeError):
                            data = {"raw": text}
                        out.setdefault(call.get("name", "?"), []).append({"ok": not b.get("is_error"), "input": call.get("input", {}), "data": data})
        return out

    @staticmethod
    def _evidence(text: str, words: List[str]) -> str:
        """First line of the material that contains one of the keywords (what the mock 'noticed')."""
        for line in text.splitlines():
            low = line.lower()
            if any(w in low for w in words):
                return line.strip()[:220]
        return ""

    @staticmethod
    def _classify(text: str) -> Dict[str, Any]:
        t = text.lower()
        vulnerable = any(w in t for w in VULN_WORDS)
        out = MockLLM._classify_inner(t, vulnerable)
        out["evidence"] = MockLLM._evidence(text, out.pop("_words", []))
        out["tenant_damage"] = MockLLM._evidence(text, TENANT_DAMAGE_WORDS)
        out["ambiguous"] = out["category"] == "heating" and "shower" in t and any(w in t for w in AMBIGUITY_WORDS)
        out["noisy"] = len(text) > 8000
        return out

    @staticmethod
    def _classify_inner(t: str, vulnerable: bool) -> Dict[str, Any]:
        if any(w in t for w in GAS_WORDS):
            return {"category": "gas", "urgency": "emergency", "trade": "gas_engineer", "safety": "gas", "vulnerable": vulnerable, "_words": GAS_WORDS}
        if any(w in t for w in ELEC_WORDS):
            return {"category": "electrical", "urgency": "emergency", "trade": "electrician", "safety": "electrical", "vulnerable": vulnerable, "_words": ELEC_WORDS}
        if any(w in t for w in APPLIANCE_WORDS) and "mould" not in t:
            urg = "urgent" if any(w in t for w in LEAK_WORDS) else "routine"
            return {"category": "appliance", "urgency": urg, "trade": "appliance_engineer", "safety": None, "vulnerable": vulnerable, "_words": APPLIANCE_WORDS}
        if any(w in t for w in MOULD_WORDS):
            return {"category": "damp_mould", "urgency": "urgent", "trade": "damp_specialist", "safety": None, "vulnerable": vulnerable, "_words": MOULD_WORDS}
        if any(w in t for w in LEAK_WORDS):
            urg = "emergency" if ("flood" in t or "pouring" in t or "can't stop" in t or "cannot stop" in t) else "urgent"
            return {"category": "plumbing", "urgency": urg, "trade": "plumber", "safety": None, "vulnerable": vulnerable, "_words": LEAK_WORDS}
        if any(w in t for w in HEAT_WORDS):
            urg = "emergency" if vulnerable else "urgent"
            return {"category": "heating", "urgency": urg, "trade": "gas_engineer", "safety": None, "vulnerable": vulnerable, "_words": HEAT_WORDS}
        if any(w in t for w in LOCK_WORDS):
            return {"category": "security", "urgency": "emergency", "trade": "locksmith", "safety": None, "vulnerable": vulnerable, "_words": LOCK_WORDS}
        return {"category": "other", "urgency": "routine", "trade": "handyperson", "safety": None, "vulnerable": vulnerable, "_words": []}

    @staticmethod
    def _property_query(text: str) -> Optional[str]:
        m = re.search(r"PROP-\d+", text)
        if m:
            return m.group(0)
        m = re.search(r"\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b", text)
        if m:
            return m.group(0)
        m = re.search(r"\d{1,4}[A-Za-z]?\s+[A-Z][a-z]+\s+(Road|Street|Lane|Avenue|Close|Gardens|Way|Drive|Place|Crescent|Terrace)", text)
        return m.group(0) if m else None

    # ----- the scripted policy -----
    def step(self, system: str, messages: List[dict], tools: List[dict]) -> LLMResponse:
        text = self._case_text(messages)
        res = self._results(messages)
        cls = self._classify(text)
        n_assistant = sum(1 for m in messages if m["role"] == "assistant")

        # Step 0: already escalated without a property -> stop
        if "lookup_property" not in res and "escalate_to_human" in res:
            return LLMResponse([_text("Escalated; nothing further can be done safely.")], "end_turn")

        # Step 1: verify property
        if "lookup_property" not in res:
            q = self._property_query(text)
            if not q:
                return LLMResponse([_text("No property identifier found in the material; I cannot verify the property."),
                                    _tool_use("escalate_to_human", {"ticket_id": "", "severity": "medium", "to": "property_manager",
                                                                   "reason": "Reporter did not identify the property and no match could be derived.",
                                                                   "handover": "Message received with no property ID/address. Ask reporter for address/postcode, then triage per policy."})],
                                   "tool_use")
            return LLMResponse([_text("Verifying the property record."), _tool_use("lookup_property", {"query": q})], "tool_use")

        prop_r = res["lookup_property"][-1]
        if prop_r["ok"] and prop_r["data"].get("found") is False:
            # Not in local records: the case file is the record. Log the case as-is and route to a human for setup.
            if "escalate_to_human" not in res:
                return LLMResponse([_text("Property is not in the local records; the case file is the system of record."),
                                    _tool_use("escalate_to_human", {"ticket_id": "", "severity": "low", "to": "property_manager",
                                                                   "reason": "Property not found in records database; case needs linking to a property record before automated booking.",
                                                                   "handover": f"Query '{prop_r['input'].get('query')}' returned no record. Case material summarised in the answer. Verify property/tenancy, then proceed per policy."})], "tool_use")
            return LLMResponse([_text("Escalated: property unverified in records.")], "end_turn")
        if not prop_r["ok"]:
            if len(res["lookup_property"]) < 2:
                # retry with a different fragment
                q2 = self._property_query(text.replace(prop_r["input"].get("query", ""), ""))
                if q2:
                    return LLMResponse([_tool_use("lookup_property", {"query": q2})], "tool_use")
            if "escalate_to_human" not in res:
                return LLMResponse([_tool_use("escalate_to_human", {"ticket_id": "", "severity": "medium", "to": "property_manager",
                                                                   "reason": "Property could not be verified in records.",
                                                                   "handover": f"Lookup failed for '{prop_r['input'].get('query')}'. Confirm the property with the reporter before any action."})], "tool_use")
            return LLMResponse([_text("Escalated: property unverified.")], "end_turn")

        prop = prop_r["data"]
        pid = prop["property_id"]

        # Step 2: tenancy + history in parallel
        if "lookup_tenancy" not in res:
            return LLMResponse([_text("Checking tenancy and repair history."),
                                _tool_use("lookup_tenancy", {"property_id": pid}),
                                _tool_use("get_repair_history", {"property_id": pid})], "tool_use")

        ten_r = res["lookup_tenancy"][-1]
        tenancy = (ten_r["data"].get("active_tenancy") if ten_r["ok"] else None) or {}
        tenant = (tenancy.get("tenants") or [{}])[0]
        injected = any(w in text.lower() for w in INJECTION_WORDS)
        if not tenancy or injected:
            if "escalate_to_human" not in res:
                why = []
                if not tenancy:
                    why.append("no ACTIVE tenancy on record - reporter may not be a current tenant")
                if injected:
                    why.append("message contains embedded instructions attempting to bypass approval (treated as untrusted)")
                return LLMResponse([_tool_use("escalate_to_human", {"ticket_id": "", "severity": "high", "to": "property_manager",
                                                                   "reason": "; ".join(why),
                                                                   "handover": f"Property {pid} ({prop.get('address')}). " + " ".join(why) + ". No booking made. Verify occupancy/landlord position before any spend."})], "tool_use")
            return LLMResponse([_text("Escalated; no action taken.")], "end_turn")
        if tenancy.get("vulnerability_notes"):
            cls["vulnerable"] = True
            if cls["urgency"] == "urgent":
                cls["urgency"] = "emergency"
        landlord_phone = prop.get("landlord_phone", "")
        landlord_email = prop.get("landlord_email", "")
        limit = prop.get("spend_limit_gbp", 250)

        # Step 3: safety rules -> escalate, do not book
        if cls["safety"] in {"gas", "electrical"}:
            if "escalate_to_human" not in res:
                advice = ("Open windows, do not use switches or naked flames, leave the property if the smell is strong, and call the National Gas Emergency line on 0800 111 999 now."
                          if cls["safety"] == "gas" else "Switch off the electricity at the consumer unit if it is safe to do so and keep away from the affected area. An emergency electrician is being arranged.")
                blocks = [_text("Safety rule applies; escalating and advising the tenant.")]
                if tenant.get("phone"):
                    blocks.append(_tool_use("send_message", {"recipient_type": "tenant", "recipient": tenant["phone"], "channel": "sms", "body": advice}))
                blocks.append(_tool_use("escalate_to_human", {"ticket_id": "", "severity": "critical", "to": "property_manager",
                                                             "reason": f"{cls['safety']} safety rule - requires certified engineer and human oversight.",
                                                             "handover": f"Property {pid} ({prop.get('address')}). Reported: {cls['category']} hazard. Tenant advised ({advice}). Needs {'Gas Safe' if cls['safety']=='gas' else 'NICEIC'} engineer today; landlord {prop.get('landlord_name')} to be informed."}))
                if landlord_email:
                    blocks.append(_tool_use("send_message", {"recipient_type": "landlord", "recipient": landlord_email, "channel": "email", "body": f"Emergency {cls['category']} report at {prop.get('address')}. Tenant advised on safety steps; property manager escalated; certified engineer being arranged."}))
                return LLMResponse(blocks, "tool_use")
            return LLMResponse([_text("Escalated under safety policy; tenant and landlord informed.")], "end_turn")

        # Step 4: ticket
        if "create_maintenance_ticket" not in res:
            return LLMResponse([_tool_use("create_maintenance_ticket", {"property_id": pid, "title": f"{cls['category']} issue reported", "category": cls["category"],
                                                                        "urgency": cls["urgency"], "description": text[:800], "reported_by": tenant.get("name", "tenant")})], "tool_use")
        ticket = res["create_maintenance_ticket"][-1]["data"]
        tid = ticket.get("ticket_id", "")

        # Step 4b: genuine ambiguity about which system failed -> one targeted question, no guess
        if cls["ambiguous"]:
            if "send_message" not in res:
                q = ("Quick check so we send the right engineer today: is the hot water from the KITCHEN tap also cold? "
                     "If the kitchen tap runs hot, the fault is the electric shower unit and we will send an electrician. "
                     "If it is cold too, it is the boiler and we will send a Gas Safe engineer. Reply 'tap hot' or 'tap cold'.")
                return LLMResponse([_text("Cannot tell whether the shower unit or the boiler failed; asking one question before booking."),
                                    _tool_use("send_message", {"recipient_type": "tenant", "recipient": tenant.get("phone") or tenant.get("email", ""),
                                                               "channel": "sms" if tenant.get("phone") else "email", "body": q}),
                                    _tool_use("record_note", {"ticket_id": tid, "note": "Awaiting tenant reply: kitchen tap hot/cold decides electrician vs gas engineer. Provisional trade: gas_engineer."})], "tool_use")
            return LLMResponse([_text("Ticket open; awaiting the tenant's answer before booking.")], "end_turn")

        # Step 5: contractors
        if "search_contractors" not in res:
            return LLMResponse([_tool_use("search_contractors", {"trade": cls["trade"], "postcode": prop.get("postcode", ""), "emergency": cls["urgency"] == "emergency"})], "tool_use")
        contractors = res["search_contractors"][-1]["data"].get("contractors", [])
        if not contractors and len(res["search_contractors"]) == 1:
            return LLMResponse([_tool_use("search_contractors", {"trade": cls["trade"], "postcode": prop.get("postcode", ""), "emergency": False})], "tool_use")
        preferred = prop.get("preferred_contractors", [])
        contractors = sorted(contractors, key=lambda c: (c["contractor_id"] not in preferred, -c.get("rating", 0)))
        tried = {r["input"]["contractor_id"] for r in res.get("check_contractor_availability", [])}
        usable = None
        for r in res.get("check_contractor_availability", []):
            if r["ok"] and r["data"].get("slots"):
                usable = r
        if usable is None:
            for c in contractors:
                if c["contractor_id"] not in tried:
                    return LLMResponse([_tool_use("check_contractor_availability", {"contractor_id": c["contractor_id"], "urgency": cls["urgency"] if cls["urgency"] in {"emergency", "urgent", "routine"} else "routine"})], "tool_use")
            if "escalate_to_human" not in res:
                return LLMResponse([_tool_use("escalate_to_human", {"ticket_id": tid, "severity": "high", "to": "property_manager",
                                                                   "reason": "No contractor availability found after trying all panel options.",
                                                                   "handover": f"Ticket {tid}: tried {sorted(tried)}; all failed/unavailable. Needs manual sourcing."})], "tool_use")
            return LLMResponse([_text("Escalated: no contractor available.")], "end_turn")

        # Step 6: approval if over limit
        est = next((c.get("call_out_gbp", 95) for c in contractors if c["contractor_id"] == usable["input"]["contractor_id"]), 95)
        if est > limit and cls["urgency"] != "emergency" and "request_landlord_approval" not in res:
            return LLMResponse([_tool_use("request_landlord_approval", {"ticket_id": tid, "landlord_id": prop.get("landlord_id", ""), "estimated_cost_gbp": est,
                                                                        "reason": f"Estimated {est} exceeds pre-authorised limit {limit}."})], "tool_use")
        if est > limit and cls["urgency"] != "emergency":
            if "send_message" not in res:
                return LLMResponse([_tool_use("send_message", {"recipient_type": "tenant", "recipient": tenant.get("phone") or tenant.get("email", ""), "channel": "sms" if tenant.get("phone") else "email",
                                                               "body": "Thanks for reporting this. We have logged the repair and are awaiting the landlord's approval for the cost; we will confirm an appointment as soon as it is approved."})], "tool_use")
            return LLMResponse([_text("Awaiting landlord approval before booking.")], "end_turn")

        # Step 7: book
        if "schedule_contractor" not in res:
            slot = usable["data"]["slots"][0]
            return LLMResponse([_tool_use("schedule_contractor", {"ticket_id": tid, "contractor_id": usable["input"]["contractor_id"], "slot_id": slot["slot_id"],
                                                                  "access_notes": tenancy.get("access_notes", "Tenant will provide access; call ahead.")})], "tool_use")
        booking = res["schedule_contractor"][-1]
        if not booking["ok"]:
            if "escalate_to_human" not in res:
                return LLMResponse([_tool_use("escalate_to_human", {"ticket_id": tid, "severity": "high", "to": "property_manager", "reason": "Booking failed.", "handover": str(booking["data"])})], "tool_use")
            return LLMResponse([_text("Booking failed; escalated.")], "end_turn")

        # Step 8: inform tenant + landlord (+ confirm by call for emergencies)
        sent = res.get("send_message", [])
        if not sent:
            slot = usable["data"]["slots"][0]
            blocks = []
            if tenant.get("phone") or tenant.get("email"):
                blocks.append(_tool_use("send_message", {"recipient_type": "tenant", "recipient": tenant.get("phone") or tenant.get("email"), "channel": "sms" if tenant.get("phone") else "email",
                                                         "body": f"Hi {tenant.get('name', '')}, we've booked {booking['data'].get('contractor_name')} for {slot['start']} (ref {booking['data'].get('booking_ref')}). They will call before arriving. Reply if that time doesn't work."}))
            if landlord_email:
                blocks.append(_tool_use("send_message", {"recipient_type": "landlord", "recipient": landlord_email, "channel": "email",
                                                         "body": f"{cls['category'].title()} repair logged at {prop.get('address')} (ticket {tid}); {booking['data'].get('contractor_name')} booked for {slot['start']}, est. £{est}."}))
            if cls["urgency"] == "emergency":
                blocks.append(_tool_use("place_call", {"to_role": "contractor", "phone": next((c.get("phone", "") for c in contractors if c["contractor_id"] == usable["input"]["contractor_id"]), ""),
                                                       "purpose": "Confirm emergency attendance", "talking_points": f"- Confirm slot {slot['start']}\n- Access: {tenancy.get('access_notes', '')}\n- Call tenant 30 min before"}))
            if blocks:
                return LLMResponse([_text("Booking confirmed; informing tenant and landlord.")] + blocks, "tool_use")
        if sent and not sent[-1]["ok"] and len(sent) < 3 and tenant.get("email"):
            return LLMResponse([_tool_use("send_message", {"recipient_type": "tenant", "recipient": tenant["email"], "channel": "email", "body": sent[-1]["input"]["body"]})], "tool_use")
        return LLMResponse([_text("Repair booked and all parties informed.")], "end_turn")

    def finalize(self, system: str, messages: List[dict], tools: List[dict], schema: dict) -> Dict[str, Any]:
        text = self._case_text(messages)
        res = self._results(messages)
        cls = self._classify(text)
        esc = res.get("escalate_to_human", [])
        booked = any(r["ok"] for r in res.get("schedule_contractor", []))
        approval = res.get("request_landlord_approval", [])
        failed = [f"{name}({r['input']}) -> {r['data']}" for name, rs in res.items() for r in rs if not r["ok"]]
        actions = [f"{name}: {json.dumps(r['input'])[:160]}" for name, rs in res.items() for r in rs if r["ok"] and name not in {"lookup_property", "lookup_tenancy", "get_repair_history", "search_contractors", "check_contractor_availability"}]
        if esc:
            decision = "escalated"
        elif booked:
            decision = "in_progress"
        elif approval:
            decision = "in_progress"
        else:
            decision = "needs_information"
        prop = (res.get("lookup_property") or [{}])[-1].get("data", {}) if res.get("lookup_property") else {}
        ten = (res.get("lookup_tenancy") or [{}])[-1].get("data", {}) if res.get("lookup_tenancy") else {}
        vuln_note = ((ten.get("active_tenancy") or {}).get("vulnerability_notes") or "") if isinstance(ten, dict) else ""
        risk = []
        if cls.get("safety"):
            risk.append(f"{cls['safety']} safety rule applied")
        if cls.get("vulnerable"):
            risk.append("vulnerable occupant")
        if vuln_note:
            risk.append(f"vulnerability: {vuln_note}")
        if any(w in text.lower() for w in INJECTION_WORDS):
            risk.append("embedded instructions in case material ignored (possible prompt injection)")
        if cls.get("tenant_damage"):
            risk.append(f"possible tenant-caused damage, recharge to consider: \"{cls['tenant_damage']}\"")
        assumptions = ["Mock LLM: keyword triage; replace with Claude for real judgement."]
        if cls.get("noisy"):
            assumptions.append("Material is long and mostly irrelevant chatter; only maintenance-related lines were used.")
        gaps = [] if res.get("lookup_property") and res["lookup_property"][-1]["ok"] else ["Property could not be verified from the material"]
        if cls.get("ambiguous"):
            gaps.append("Whether the kitchen hot tap is also cold - decides electric shower (electrician) vs boiler (Gas Safe engineer)")
        return {
            "case_summary": f"Reported {cls['category']} issue at {prop.get('address', 'unverified property')}. Urgency assessed as {cls['urgency']}." + (f" Evidence: \"{cls['evidence']}\"" if cls.get("evidence") else "") + (f" Vulnerability: {vuln_note}" if vuln_note else ""),
            "issue_category": cls["category"],
            "urgency": cls["urgency"] if cls["urgency"] in {"emergency", "urgent", "routine"} else "unclear",
            "decision": decision,
            "outcome": ("Escalated to a human with handover: " + esc[-1]["input"]["reason"]) if esc else ("Contractor booked and parties informed." if booked else ("Awaiting landlord approval." if approval else "Blocked pending information: " + (gaps[-1] if gaps else "see information_gaps"))),
            "actions_taken": actions,
            "failed_actions": failed,
            "escalation": {"required": bool(esc), "to": esc[-1]["input"]["to"] if esc else "", "reason": esc[-1]["input"]["reason"] if esc else "", "handover": esc[-1]["input"]["handover"] if esc else ""},
            "conflicts": [],
            "information_gaps": gaps,
            "assumptions": assumptions,
            "tenant_communication": next((r["input"]["body"] for r in res.get("send_message", []) if r["ok"] and r["input"]["recipient_type"] == "tenant"), "none"),
            "landlord_communication": next((r["input"]["body"] for r in res.get("send_message", []) if r["ok"] and r["input"]["recipient_type"] == "landlord"), "none"),
            "next_steps": ["Contractor attends; confirm completion with tenant"] if booked else (["Human reviews escalation"] if esc else ["Await approval / information"]),
            "risk_flags": risk,
            "confidence": 0.6,
            "reasoning": "Rule-based mock: classified by keywords, verified property, applied safety/approval rules from policy, booked first available contractor from preferred list.",
        }
