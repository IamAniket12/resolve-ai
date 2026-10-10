"""Turn public example cases into decision-point test cases, as the public repo README advises:

  1. choose a decision point in the history
  2. give the system only the events and attachments available at that point
  3. hide later events and any summary or outcome that reveals the ending

Usage:
  python scripts/cut_public_case.py "<path to track folder>" data/public_cut --events 3
  python scripts/cut_public_case.py "<track folder>" data/public_cut --only 002 025 --events 6

--events N      keep the first N events of history.md (default 3: the request, intake classification, first system step)
--fraction F    instead keep the first F of the events (0.0-1.0)
Overview, Outcome, Status/Updated/Completed lines are stripped from index.md. The original index.md and the
hidden tail of the history are saved under <out>_answers/<case>/ for later comparison, never under the case folder.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

EVENT_RE = re.compile(r'<a id="event-(\d+)"></a>')


def split_events(history: str):
    """Return (header, [event_text, ...]) where each event starts at its anchor."""
    idx = [m.start() for m in EVENT_RE.finditer(history)]
    if not idx:
        return history, []
    header = history[: idx[0]]
    events = [history[a:b] for a, b in zip(idx, idx[1:] + [len(history)])]
    return header, events


def strip_index(index: str) -> str:
    out = []
    skip = False
    for line in index.splitlines():
        if line.startswith("## "):
            skip = line.strip() in {"## Overview", "## Outcome", "## History"}
            if skip:
                continue
        if skip:
            continue
        if re.match(r"- \*\*(Status|Updated|Completed):\*\*", line):
            continue
        out.append(line)
    text = "\n".join(out).rstrip() + "\n"
    return re.sub(r"\n{3,}", "\n\n", text)


def cut_case(src: Path, dst_root: Path, events_keep: int | None, fraction: float | None) -> tuple[int, int]:
    dst = dst_root / src.name
    ans = dst_root.parent / (dst_root.name + "_answers") / src.name
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    ans.mkdir(parents=True, exist_ok=True)

    index = (src / "index.md").read_text(encoding="utf-8", errors="replace")
    (dst / "index.md").write_text(strip_index(index), encoding="utf-8")
    (ans / "index_full.md").write_text(index, encoding="utf-8")

    history = (src / "history.md").read_text(encoding="utf-8", errors="replace")
    header, events = split_events(history)
    n = len(events)
    keep = max(1, int(round(n * fraction))) if fraction is not None else min(n, events_keep or 3)
    header = re.sub(r"Total events: \d+", f"Events so far: {keep}", header)
    (dst / "history.md").write_text(header + "".join(events[:keep]).rstrip() + "\n", encoding="utf-8")
    (ans / "history_hidden_tail.md").write_text("".join(events[keep:]), encoding="utf-8")

    att = src / "attachments"
    if att.exists():
        shutil.copytree(att, dst / "attachments")
    return keep, n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("track_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--events", type=int, default=3)
    ap.add_argument("--fraction", type=float)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--random", type=int, help="pick this many cases at random")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--at-reply", action="store_true",
                    help="cut right after an inbound message (landlord/tenant/contractor), at a random point, so the next event is the agency's move")
    a = ap.parse_args()
    track = Path(a.track_dir)
    out = Path(a.out_dir)
    cases = sorted(p for p in track.iterdir() if p.is_dir() and (p / "index.md").exists())
    if a.only:
        cases = [c for c in cases if c.name in set(a.only)]
    import random
    rng = random.Random(a.seed)
    if a.random:
        cases = sorted(rng.sample(cases, min(a.random, len(cases))), key=lambda p: p.name)
    for c in cases:
        events_keep = a.events
        if a.at_reply:
            _, evs = split_events((c / "history.md").read_text(encoding="utf-8", errors="replace"))
            inbound = [i + 1 for i, e in enumerate(evs)
                       if re.search(r"\*\*From:\*\* (Landlord|Tenant|Contractor|Maintenance|Provider)", e)
                       and 3 <= i + 1 <= len(evs) - 2]
            events_keep = rng.choice(inbound) if inbound else 3
        keep, n = cut_case(c, out, events_keep, a.fraction)
        print(f"{c.name}: kept {keep}/{n} events")


if __name__ == "__main__":
    main()
