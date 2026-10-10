"""The case file is the system of record.

Event cases arrive as index.md + history.md + attachments, with people named but no database behind them.
This backend answers the records tools (property, tenancy, repair history, contractors) FROM THE CASE FILE
and from the other cases in the same batch, and delegates every action tool to the inner backend
(mock or HTTP). The agent therefore never meets "property not found" on real data.

What it extracts (heuristics, all labelled as such in the results):
- property: the "Property:" line of the index, else the first UK-looking address in the material
- parties: tenant / landlord / contractor names from greetings and "Our maintenance provider X" lines,
  plus the names of the agency staff who have handled the case
- prior jobs: other cases in the batch at the same address (title, created, outcome when present)
- providers: contractors used anywhere in the batch, with the trade inferred from the case titles
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

from resolve_ai.models import CaseBundle

ADDRESS_RE = re.compile(r"\*\*Property:\*\*\s*(.+)")
UK_ADDRESS_RE = re.compile(r"(?:Flat \d+[A-Za-z]?,\s*)?\d+[A-Za-z]?\s+[A-Z][A-Za-z']+(?:\s+[A-Z][A-Za-z']+)*,\s*[A-Z][A-Za-z']+,\s*[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}")
POSTCODE_RE = re.compile(r"\b([A-Z]{1,2}\d{1,2}[A-Z]?)\s*(\d[A-Z]{2})\b")
EVENT_RE = re.compile(
    r"## (?P<ts>[\d\-: ]+UTC) — event (?P<n>\d+)\n\n- \*\*Channel:\*\* (?P<ch>[^\n]+)\n- \*\*From:\*\* (?P<frm>[^\n]+)\n- \*\*To:\*\* (?P<to>[^\n]+)\n\n(?P<body>.*?)(?=\n<a id=\"event-|\Z)",
    re.S,
)
GREETING_RE = re.compile(r"^(?:Hi|Hello|Dear|Good morning|Good afternoon|Morning|Afternoon|HI)[,]?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)[,.!]?\s*$", re.M)
PROVIDER_RE = re.compile(r"(?:Our maintenance provider|maintenance provider|contractor,)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,2}?)(?=\s+(?:will|has|is|to)\b)")
HOLD_BY_RE = re.compile(r"Put on hold by ([A-Z][a-z]+ [A-Z][a-z]+)")
TENANT_NAME_RE = re.compile(r"Tenant Name:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)")
SOURCE_ROLE_RE = re.compile(r"\*\*Source role:\*\*\s*(.+)")
CREATED_RE = re.compile(r"\*\*Created:\*\*\s*(.+)")
TITLE_RE = re.compile(r"^#\s*(.+)$", re.M)
SECTION_RE = re.compile(r"^## (Overview|Outcome)\n\n(.*?)(?=\n## |\Z)", re.S | re.M)

TRADE_HINTS = [
    ("gas_engineer", ["boiler", "gas", "heating", "radiator", "hot water"]),
    ("plumber", ["toilet", "tap", "leak", "drain", "shower", "basin", "pipe", "plumb", "sink", "bath"]),
    ("electrician", ["electric", "light", "socket", "extractor", "fuse", "power"]),
    ("appliance_engineer", ["washing machine", "dishwasher", "oven", "fridge", "cooker", "hob", "appliance", "dryer"]),
    ("locksmith", ["lock", "key", "door"]),
    ("glazier", ["window", "glass", "handle"]),
    ("handyperson", ["clean", "garden", "hedge", "paint", "carpet", "shelf", "general", "check-out", "checkout", "repair"]),
    ("damp_specialist", ["damp", "mould", "mold", "condensation"]),
    ("pest_control", ["pest", "mice", "rat", "wasp", "ant"]),
    ("roofer", ["roof", "gutter", "tile"]),
    ("drainage", ["blocked", "drain", "sewer"]),
]


def _text_of(bundle: CaseBundle, name_part: str) -> str:
    for a in bundle.attachments:
        if name_part in a.name.lower():
            return a.text or ""
    return ""


def _all_text(bundle: CaseBundle) -> str:
    return "\n".join(a.text or "" for a in bundle.attachments)


def infer_trade(text: str) -> str:
    t = text.lower()
    best, score = "handyperson", 0
    for trade, words in TRADE_HINTS:
        s = sum(t.count(w) for w in words)
        if s > score:
            best, score = trade, s
    return best


class CaseFacts:
    """Everything we can read off one case file, computed once."""

    def __init__(self, bundle: CaseBundle):
        self.bundle = bundle
        index = _text_of(bundle, "index")
        history = _text_of(bundle, "history")
        everything = _all_text(bundle)
        self.title = (TITLE_RE.search(index).group(1).strip() if TITLE_RE.search(index) else bundle.case_id)
        m = ADDRESS_RE.search(index) or ADDRESS_RE.search(everything)
        self.address = m.group(1).strip() if m else (UK_ADDRESS_RE.search(everything).group(0) if UK_ADDRESS_RE.search(everything) else "")
        pm = POSTCODE_RE.search(self.address or everything)
        self.postcode = f"{pm.group(1)} {pm.group(2)}" if pm else ""
        self.source_role = (SOURCE_ROLE_RE.search(index).group(1).strip() if SOURCE_ROLE_RE.search(index) else "")
        self.created = (CREATED_RE.search(index).group(1).strip() if CREATED_RE.search(index) else "")
        self.summary_sections = {k: v.strip() for k, v in SECTION_RE.findall(index)}

        tenants: Counter = Counter()
        landlords: Counter = Counter()
        providers: Counter = Counter()
        staff: Counter = Counter()
        self.events: List[Dict[str, str]] = []
        for ev in EVENT_RE.finditer(history):
            frm, to, body, ch = ev["frm"].strip(), ev["to"].strip(), ev["body"], ev["ch"].strip()
            self.events.append({"n": ev["n"], "ts": ev["ts"].strip(), "channel": ch, "from": frm, "to": to})
            for g in GREETING_RE.findall(body):
                if to.lower().startswith("tenant"):
                    tenants[g] += 1
                elif to.lower().startswith("landlord"):
                    landlords[g] += 1
                elif to.lower().startswith(("contractor", "maintenance", "provider")) or (to not in {"Not specified", "Unspecified"} and not to.lower().startswith(("agency", "northbridge"))):
                    providers[g] += 1
            for g in TENANT_NAME_RE.findall(body):
                tenants[g] += 2
            for g in PROVIDER_RE.findall(body):
                providers[g] += 2
            for g in HOLD_BY_RE.findall(body):
                staff[g] += 1
            if to not in {"Not specified", "Unspecified", "Tenant", "Landlord", "Contractor", "Agency / system"} and not to.lower().startswith(("agency", "northbridge")) and ch in {"Email", "SMS"}:
                providers[to] += 1
        self.tenants = [n for n, _ in tenants.most_common(3)]
        self.landlords = [n for n, _ in landlords.most_common(2)]
        self.providers = [n for n, _ in providers.most_common(4) if n not in self.tenants and n not in self.landlords]
        self.staff = [n for n, _ in staff.most_common(2)]
        self.last_event_ts = self.events[-1]["ts"] if self.events else ""
        self.trade = infer_trade(self.title + " " + index[:1500])


class CaseIndex:
    """Facts for every case in the batch, keyed by address, so other cases at the same property become history."""

    def __init__(self, bundles: List[CaseBundle]):
        self.facts: Dict[str, CaseFacts] = {}
        self.by_address: Dict[str, List[str]] = defaultdict(list)
        self.providers: Counter = Counter()
        self.provider_trades: Dict[str, Counter] = defaultdict(Counter)
        for b in bundles:
            try:
                f = CaseFacts(b)
            except Exception:  # noqa: BLE001
                continue
            self.facts[b.case_id] = f
            if f.address:
                self.by_address[_norm(f.address)].append(b.case_id)
            for p in f.providers:
                self.providers[p] += 1
                self.provider_trades[p][f.trade] += 1

    def facts_for(self, bundle: CaseBundle) -> CaseFacts:
        if bundle.case_id not in self.facts:
            self.facts[bundle.case_id] = CaseFacts(bundle)
        return self.facts[bundle.case_id]

    def other_cases_at(self, address: str, exclude: str) -> List[dict]:
        out = []
        for cid in self.by_address.get(_norm(address), []):
            if cid == exclude:
                continue
            f = self.facts[cid]
            out.append({"case_id": cid, "title": f.title, "created": f.created, "source_role": f.source_role,
                        "outcome": f.summary_sections.get("Outcome", "")[:400]})
        return out


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


class CaseFileBackend:
    """Records from the case file + batch; actions delegated to `inner` (MockBackend or CompositeBackend)."""

    def __init__(self, inner, bundle: CaseBundle, index: Optional[CaseIndex] = None):
        self.inner = inner
        self.bundle = bundle
        self.index = index or CaseIndex([bundle])
        self.facts = self.index.facts_for(bundle)
        self._register_named_contractors()

    def _register_named_contractors(self) -> None:
        """Contractors named in this case or used elsewhere in the batch become bookable in the inner backend,
        so availability checks and bookings against them work like any panel contractor."""
        contractors = getattr(self.inner, "contractors", None)
        if contractors is None:  # e.g. an HTTP composite without a mock list
            return
        known = {c["contractor_id"] for c in contractors}
        for i, p in enumerate(self.facts.providers):
            cid = f"NAMED-{i + 1}"
            if cid not in known:
                contractors.append({"contractor_id": cid, "name": p, "trades": [self.facts.trade], "certifications": [],
                                    "postcode_areas": [], "rating": 0, "emergency": True, "call_out_gbp": None,
                                    "phone": "", "email": "", "source": "named in this case file",
                                    "note": "Already involved in this case: prefer for continuity, warranty or an open quote. Contact via platform record."})
        i = 0
        for p, n in self.index.providers.most_common(12):
            if p in self.facts.providers:
                continue
            i += 1
            cid = f"BATCH-{i}"
            if cid not in known:
                contractors.append({"contractor_id": cid, "name": p, "trades": [t for t, _ in self.index.provider_trades[p].most_common(2)],
                                    "certifications": [], "postcode_areas": [], "rating": 0, "emergency": True, "call_out_gbp": None,
                                    "phone": "", "email": "", "source": f"used by the agency in {n} other case(s) in this batch"})

    # ---- records tools, answered from the case file ----
    def lookup_property(self, query: str) -> dict:
        f = self.facts
        # If the inner backend knows this property (our own sample data), prefer its richer record.
        try:
            inner = self.inner.lookup_property(query)
            if inner.get("found"):
                return inner
        except Exception:  # noqa: BLE001
            pass
        if not f.address:
            return {"found": False, "query": query, "note": "No property address could be read from the case file either. Ask the reporter for the address."}
        return {
            "found": True, "source": "case file", "property_id": f"CASE-{self.bundle.case_id}", "address": f.address,
            "postcode": f.postcode, "case_title": f.title, "case_created": f.created, "reported_by_role": f.source_role,
            "landlord_name": ", ".join(f.landlords) or "not named yet in the case file (address messages to 'Landlord')",
            "landlord_instructions": "none on file; follow the standard landlord approval step", "spend_limit_gbp": 250,
            "preferred_contractors": f.providers[:2],
            "agency_staff_on_case": f.staff,
            "note": "Record built from the case file (names as they appear in it). The platform holds contact details: address messages by name or role.",
        }

    def lookup_tenancy(self, property_id: str) -> dict:
        f = self.facts
        try:
            inner = self.inner.lookup_tenancy(property_id)
            if inner.get("active_tenancy"):
                return inner
        except Exception:  # noqa: BLE001
            pass
        tenants = [{"name": n, "phone": "", "email": "", "contact": "via platform record (address messages by name)"} for n in f.tenants] or \
                  [{"name": "Tenant (not named in the case file)", "phone": "", "email": "", "contact": "via platform record"}]
        return {"found": True, "source": "case file", "property_id": property_id, "status": "active (assumed: the case was raised by/for a current occupier)",
                "active_tenancy": {"tenancy_id": f"CASE-{self.bundle.case_id}", "status": "active", "tenants": tenants,
                                   "vulnerability_notes": "", "access_notes": "see the case history for access arrangements and pets"},
                "note": "Tenancy inferred from the case file; verify end dates or vulnerabilities only if the case raises them."}

    def get_repair_history(self, property_id: str) -> dict:
        f = self.facts
        jobs = []
        try:
            inner = self.inner.get_repair_history(property_id)
            jobs = inner.get("jobs", [])
        except Exception:  # noqa: BLE001
            pass
        others = self.index.other_cases_at(f.address, exclude=self.bundle.case_id) if f.address else []
        return {"property_id": property_id, "jobs": jobs, "other_cases_at_this_address": others,
                "events_in_this_case": len(f.events), "last_event": f.last_event_ts,
                "note": ("No other cases at this address in the batch; the history inside this case file is the full record."
                         if not others and not jobs else "Prior work exists: check warranties and repeat faults before paying for a new job.")}

    def search_contractors(self, trade: str, postcode: str, emergency: bool) -> dict:
        base = self.inner.search_contractors(trade, postcode, emergency)
        hits = base.get("contractors", [])
        order = {"NAMED": 0, "BATCH": 1}
        hits.sort(key=lambda c: (order.get(str(c.get("contractor_id", "")).split("-")[0], 2), -(c.get("rating") or 0)))
        note = base.get("note", "")
        if any(str(c.get("contractor_id", "")).startswith("NAMED") for c in hits):
            note = "Contractors already named in this case come first; then ones the agency used in other cases; then the panel. " + note
        return {**base, "contractors": hits, "note": note.strip()}

    # ---- everything else: delegate ----
    def __getattr__(self, name: str):
        return getattr(self.inner, name)
