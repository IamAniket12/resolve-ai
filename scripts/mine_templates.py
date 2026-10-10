"""Mine the public example histories for the agency's standard messages and workflow states.

Usage: python scripts/mine_templates.py "data/public_cases/Property Management" > docs/event/ops_templates.md

Prints a markdown digest: system update strings, hold reasons, and the most common agency emails/SMS
to landlords, tenants and contractors (deduplicated after masking names, addresses and dates).
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

EVENT_RE = re.compile(
    r'<a id="event-(\d+)"></a>\n## (?P<ts>[\d\-: ]+UTC) — event \d+\n\n'
    r"- \*\*Channel:\*\* (?P<channel>[^\n]+)\n- \*\*From:\*\* (?P<frm>[^\n]+)\n- \*\*To:\*\* (?P<to>[^\n]+)\n\n(?P<body>.*?)(?=\n<a id=\"event-|\Z)",
    re.S,
)


def mask(text: str) -> str:
    t = text
    t = re.sub(r"Flat \d+, \d+ [A-Z][a-z]+ [A-Z][a-z]+, [A-Z][a-z]+, ZZ\d \d[A-Z]{2}", "<ADDRESS>", t)
    t = re.sub(r"\d+ [A-Z][a-z]+ (Road|Street|Lane|Close|Walk|Quay|Mews|Avenue|View), [A-Z][a-z]+, ZZ\d \d[A-Z]{2}", "<ADDRESS>", t)
    t = re.sub(r"ZZ\d \d[A-Z]{2}", "<POSTCODE>", t)
    t = re.sub(r"\b\d{1,2}/\d{1,2}/\d{4}\b", "<DATE>", t)
    t = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "<DATE>", t)
    t = re.sub(r"\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b", "<DATE>", t)
    t = re.sub(r"\b0?7\d{3} \d{6}\b", "<PHONE>", t)
    t = re.sub(r"synthetic-[0-9a-f]+", "<REF>", t)
    t = re.sub(r"(Hi|Hello|Dear|Good morning,?|Good afternoon,?|Morning|Afternoon) [A-Z][a-z]+( [A-Z][a-z]+)?", r"\1 <NAME>", t)
    t = re.sub(r"this is [A-Z][a-z]+ [A-Z][a-z]+", "this is <AGENT>", t)
    t = re.sub(r"(Put on hold by) [A-Z][a-z]+ [A-Z][a-z]+", r"\1 <AGENT>", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main(track: Path) -> None:
    updates: Counter = Counter()
    holds: Counter = Counter()
    hold_reasons: Counter = Counter()
    msgs: dict = defaultdict(Counter)
    examples: dict = {}
    n_cases = 0
    for case in sorted(p for p in track.iterdir() if p.is_dir()):
        h = case / "history.md"
        if not h.exists():
            continue
        n_cases += 1
        for m in EVENT_RE.finditer(h.read_text(encoding="utf-8", errors="replace")):
            ch, frm, to, body = m["channel"].strip(), m["frm"].strip(), m["to"].strip(), m["body"].strip()
            masked = mask(body)
            if ch == "Update":
                updates[masked] += 1
            elif ch == "Hold":
                holds[masked] += 1
                r = re.search(r"Reason: ([^.]+)\.", body)
                if r:
                    hold_reasons[r.group(1).strip()] += 1
            elif ch in {"Email", "SMS"} and frm.startswith(("Agency", "Northbridge", "Juniper")):
                key = f"{ch} to {to}"
                sig = masked[:160]
                msgs[key][sig] += 1
                examples.setdefault((key, sig), body.strip())

    print(f"# Agency message and state digest\n\nMined from {n_cases} public Property Management cases. Names, addresses and dates masked.\n")
    print("## System update strings (workflow states)\n")
    for s, c in updates.most_common(25):
        print(f"- ({c}) {s}")
    print("\n## Hold reasons\n")
    for s, c in hold_reasons.most_common():
        print(f"- ({c}) {s}")
    print("\n## Hold comments (sample)\n")
    for s, c in holds.most_common(15):
        print(f"- ({c}) {s}")
    for key in sorted(msgs):
        print(f"\n## {key} (top openings)\n")
        for sig, c in msgs[key].most_common(8):
            ex = examples[(key, sig)]
            print(f"- ({c}) {sig}")
            print("\n  ```")
            print("  " + ex[:700].replace("\n", "\n  "))
            print("  ```\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
