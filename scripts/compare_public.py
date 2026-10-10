"""Compare a run on cut public cases with what the agency really did next (the hidden tail).

Usage: python scripts/compare_public.py <run_id> [--answers data/public_cut_answers] [--next 6]

For each case prints the agent's decision/status/parties contacted next to the real next events, and a
rough score: parties the real team contacted within the next N events that the agent also contacted,
plus flags for escalations the real team did not make and bookings the real team did not make.
Heuristic only: it does not know whether the agent's wording or reasoning was right.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EV = re.compile(r"## (?P<ts>[\d\-: ]+UTC) — event \d+\n\n- \*\*Channel:\*\* (?P<ch>[^\n]+)\n- \*\*From:\*\* (?P<frm>[^\n]+)\n- \*\*To:\*\* (?P<to>[^\n]+)\n\n(?P<body>.*?)(?=\n<a id=\"event-|\Z)", re.S)


def role(s: str) -> str:
    s = s.lower()
    for r in ("tenant", "landlord", "contractor", "provider"):
        if r in s:
            return "contractor" if r == "provider" else r
    return "other"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    ap.add_argument("--answers", default="data/public_cut_answers")
    ap.add_argument("--next", type=int, default=6)
    a = ap.parse_args()
    total = hits = 0
    flags = []
    n1_total = n1_channel = n1_to = 0
    CH = {"email": "email", "sms": "sms", "call": "call", "note": "note", "hold": "hold", "update": "status_update"}
    for tr in sorted(Path("logs", a.run_id).glob("*/trace.json")):
        t = json.loads(tr.read_text())
        cid = t["case_id"]
        r = t["resolution"]
        tail_p = Path(a.answers, cid, "history_hidden_tail.md")
        if not tail_p.exists():
            continue
        tail = list(EV.finditer(tail_p.read_text()))
        real_parties = {role(m["to"]) for m in tail[: a.next] if m["ch"] in {"Email", "SMS", "Call"} and m["frm"].lower().startswith(("agency", "northbridge", "juniper", "cedar", "harbour", "lantern", "oakfield"))}
        real_parties.discard("other")
        agent_parties = {e["input"].get("recipient_type") or e["input"].get("to_role") for e in t["tool_events"] if e["ok"] and e["name"] in {"send_message", "place_call", "request_landlord_approval"}}
        if any(e["ok"] and e["name"] == "request_landlord_approval" for e in t["tool_events"]):
            agent_parties.add("landlord")
        agent_parties = {p for p in agent_parties if p}
        booked = any(e["ok"] and e["name"] == "schedule_contractor" for e in t["tool_events"])
        real_booked = any("provider assigned" in m["body"].lower() or "appointment" in m["body"].lower() for m in tail[: a.next])
        real_escalated = any("review manually" in m["body"].lower() or "supervisor" in m["body"].lower() for m in tail[: a.next])
        overlap = real_parties & agent_parties
        total += len(real_parties)
        hits += len(overlap)
        st = next((e["input"] for e in reversed(t["tool_events"]) if e["name"] == "update_case_status" and e["ok"]), {})
        # n+1: the next event the AGENCY took (skipping automated system Updates), vs the agent's declared next_action
        real_n1 = next((m for m in tail if m["ch"] != "Update" and (m["frm"].lower().startswith(("agency", "northbridge", "juniper", "cedar", "harbour", "lantern", "oakfield")) or m["ch"] == "Hold")), None)
        na = r.get("next_action") or {}
        bundle = r.get("next_actions") or ([na] if na else [])
        if real_n1 is not None and bundle:
            from datetime import datetime, timedelta
            t0 = datetime.strptime(real_n1["ts"].strip(), "%Y-%m-%d %H:%M:%S UTC")
            moment = [m for m in tail if m["ch"] != "Update" and abs(datetime.strptime(m["ts"].strip(), "%Y-%m-%d %H:%M:%S UTC") - t0) <= timedelta(minutes=10)
                      and (m["frm"].lower().startswith(("agency", "northbridge", "juniper", "cedar", "harbour", "lantern", "oakfield", "keystone", "meadow")) or m["ch"] == "Hold")]
            def matches(m, a):
                rch = CH.get(m["ch"].strip().lower(), m["ch"].lower())
                rto = role(m["to"]) if m["ch"] in {"Email", "SMS", "Call"} else "agency"
                ch_ok = (a.get("channel") == rch) or (rch == "hold" and a.get("channel") in {"hold", "status_update"}) or (rch == "note" and a.get("channel") in {"note", "status_update"})
                to_ok = (a.get("to") == rto) or (rto == "agency" and a.get("to") in {"agency", "none"}) or (rch == "hold" and ch_ok)
                return ch_ok, to_ok
            n1_total += 1
            covered_ch = all(any(matches(m, a)[0] for a in bundle) for m in moment)
            covered_to = all(all(matches(m, a)) for m in moment for a in [max(bundle, key=lambda a: sum(matches(m, a)))])
            n1_channel += covered_ch; n1_to += covered_to
            agent_desc = " + ".join(f"{a.get('channel')}→{a.get('to')}" for a in bundle)
            real_desc = " + ".join(f"{m['ch']}→{m['to'][:10]}" for m in moment)
            print(f"   n+1 agent: {agent_desc} | real moment ({len(moment)}): {real_desc} :: {re.sub(r'\s+', ' ', real_n1['body'])[:90]}  [{'covered' if covered_ch and covered_to else 'partial' if covered_ch or covered_to else 'X'}]")
        print(f"== {cid}: agent {r['decision']} / status {st.get('status', '-')} | contacted {sorted(agent_parties)} | real next contacted {sorted(real_parties)} | overlap {sorted(overlap)}")
        if r["escalation"]["required"] and not real_escalated:
            flags.append(f"{cid}: agent escalated, real team did not (reason: {r['escalation']['reason'][:120]})")
        if booked and not real_booked:
            flags.append(f"{cid}: agent booked a contractor; real team had not booked within the next {a.next} events")
        if real_parties and not overlap:
            flags.append(f"{cid}: agent contacted nobody the real team contacted next")
    print(f"\nn+1 moment covered: by channel {n1_channel}/{n1_total}, by channel+recipient {n1_to}/{n1_total}")
    print(f"parties overlap within next {a.next} events: {hits}/{total}")
    print("flags:" if flags else "flags: none")
    for f in flags:
        print(" -", f)


if __name__ == "__main__":
    main()
