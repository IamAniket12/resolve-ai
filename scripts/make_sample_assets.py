"""Regenerate the generated attachments for sample cases 07 and 08.

Run:  python scripts/make_sample_assets.py

07_noisy_group_chat         -> whatsapp_group_export.txt   (~30k chars, two real issues buried in chatter)
08_large_context_washing_machine -> inventory.pdf (6 pages), repair_log.csv (60 rows), photo_kitchen_floor.png

Everything is deterministic (seeded) so the files are stable in git.
"""
from __future__ import annotations

import csv
import random
import struct
import zlib
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "sample_cases"

# ----------------------------------------------------------------------------
# 07: WhatsApp group export, noisy, two real issues buried near the end
# ----------------------------------------------------------------------------

PEOPLE = ["Josh", "Priya", "Ben"]
FILLER = [
    "anyone home to take a parcel this afternoon?", "yes I'm in till 3", "who finished the oat milk 😤",
    "not me", "lol", "bins go out tonight, it's the brown bin week", "did it already", "legend",
    "the guy next door is drilling AGAIN", "it's 9pm, that's taking the piss", "film night Friday?",
    "I'm out Friday, Saturday?", "Sat works", "can someone let the window cleaner in Thursday morning",
    "I've got a 9am but I'll leave the gate unlocked", "cheers", "wifi's being slow again", "restarted it",
    "better now", "rent went out, just checking everyone's did", "yep", "mine too", "has anyone seen my grey hoodie",
    "on the airer in the back room", "ta", "ordered a new shower curtain, the old one is grim", "good shout",
    "pub quiz Tuesday, we need a third", "I'm in", "neighbour's cat is in our garden again", "it's cute leave it",
    "going Tesco, need anything?", "milk and bin bags pls", "and biscuits", "done", "who's got the spare key?",
    "me, it's on the hook by the door", "heating timer is set to come on at 6, is that ok for everyone?",
    "fine by me", "can we do 6:30 instead", "sure", "the council sent a letter about the recycling changes",
    "I put it on the fridge", "train strike Thursday fyi", "ugh", "working from home then",
    "there's a weird smell in the hall, think it's the neighbour's cooking", "yeah it's always curry Wednesdays, I'm not mad",
    "Deliveroo's here", "coming", "can everyone keep the back door locked, there were break-ins on Alma Rd",
    "will do", "noted", "I'm away next week, water my basil pls", "🌿", "match is on at 8 if anyone wants to watch",
    "I'll join for the second half", "my room's freezing, is the radiator on in yours?", "yeah mine's warm",
    "bled it, it's fine now", "nice one", "anyone want my old desk chair, getting a new one", "me!",
    "landlord said she'd pop by to check the smoke alarms sometime this month", "ok", "the gutter is dripping outside my window when it rains, not urgent just annoying",
    "mention it to the agency when we message them about the fan", "yeah will do",
]

KEY_MESSAGES = [
    # (offset from end, person, text)
    (140, "Priya", "btw the bathroom extractor fan has stopped working completely, it's not just noisy any more. the ceiling above the shower has black mould patches now, it's spreading onto the wall"),
    (139, "Josh", "yeah I noticed, it's been dead about 2 weeks. I've been opening the window but it's not enough"),
    (138, "Ben", "my asthma's been worse this month, not sure if it's that but probably doesn't help"),
    (90, "Priya", "also I need to own up - I dropped the cast iron pan on the hob yesterday and the glass has a big crack across the back left ring. the other rings work but I'm not using the cracked one. sorry 🙈 I know that's on me"),
    (89, "Josh", "oof. that's gonna be a deposit thing probably"),
    (88, "Priya", "yeah I'll cover it, just want it sorted before it gets worse"),
    (30, "Ben", "ok so for the agency message: 1) extractor fan dead + mould in bathroom 2) cracked hob glass (Priya's). anything else?"),
    (29, "Josh", "the gutter thing but that's minor"),
    (28, "Priya", "send it, someone's always home after 4 for access"),
    (1, "Ben", "sent to maintenance@ with this whole chat export attached so they have the context"),
]


def make_group_chat() -> str:
    rng = random.Random(7)
    n = 600
    key = {n - off: (who, text) for off, who, text in KEY_MESSAGES}
    t = datetime(2026, 8, 20, 8, 3)
    lines = ["WhatsApp chat export: 'Linden Grove house 🏠'", "Exported 10/10/2026 by Ben Okoro", ""]
    for i in range(n):
        t += timedelta(minutes=rng.randint(2, 180))
        if i in key:
            who, text = key[i]
        else:
            who, text = rng.choice(PEOPLE), rng.choice(FILLER)
        lines.append(f"[{t:%d/%m/%Y, %H:%M}] {who}: {text}")
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------
# 08: inventory PDF (hand-built PDF writer, no reportlab needed)
# ----------------------------------------------------------------------------

def _pdf_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(pages: list[list[str]], out: Path) -> None:
    objs: list[bytes] = []

    def add(b: bytes) -> int:
        objs.append(b)
        return len(objs)

    font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_ids = []
    content_ids = []
    for lines in pages:
        y = 800
        parts = ["BT", "/F1 10 Tf", "12 TL", f"50 {y} Td"]
        for ln in lines:
            parts.append(f"({_pdf_escape(ln)}) Tj T*")
        parts.append("ET")
        stream = "\n".join(parts).encode("latin-1", "replace")
        cid = add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        content_ids.append(cid)
        page_ids.append(len(objs) + 1)
        objs.append(b"")  # placeholder, filled after pages obj id known
    pages_id = len(objs) + 1
    objs.append(b"")
    for pid, cid in zip(page_ids, content_ids):
        objs[pid - 1] = (f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 595 842] "
                         f"/Resources << /Font << /F1 {font} 0 R >> >> /Contents {cid} 0 R >>").encode()
    kids = " ".join(f"{p} 0 R" for p in page_ids)
    objs[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    catalog = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())

    buf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(len(buf))
        buf += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(buf)
    buf += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        buf += f"{off:010d} 00000 n \n".encode()
    buf += f"trailer\n<< /Size {len(objs) + 1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    out.write_bytes(bytes(buf))


ROOMS = {
    "Hallway": ["Walls: magnolia emulsion, good", "Floor: laminate, light scuffing near door", "Ceiling: white, good", "Smoke alarm: mains, tested OK",
                "Light fitting: pendant, working", "Radiator: single panel, working", "Door: fire door, closer working", "Coat hooks x3"],
    "Living room": ["Walls: magnolia, small scuff behind sofa", "Floor: laminate, good", "Window: uPVC double glazed, both handles OK, blind good",
                    "Radiator: double panel, TRV fitted", "Sofa: 3-seat grey fabric, good", "TV unit: oak effect, good", "Coffee table: oak effect, ring mark",
                    "Curtains: none", "Sockets: 6 double, all tested", "Light: 3-spot bar, working"],
    "Kitchen": ["Walls: tiled splashback, good; painted walls good", "Floor: vinyl, good at check-in", "Worktops: laminate, chip near sink",
                "Sink: stainless, mixer tap, working", "Oven: Beko BBXIF22100S, clean, working", "Hob: Beko induction, working",
                "Extractor: integrated, working, filter clean", "Fridge freezer: Beko integrated, working",
                "Washing machine: Beko WTK94121W (supplied new 2024-03), working, no leaks at check-in", "Dishwasher: none",
                "Boiler: Vaillant ecoTEC (cupboard), pressure 1.4 bar", "Sockets: 5 double, tested", "Bin: none supplied"],
    "Bedroom 1": ["Walls: magnolia, good", "Carpet: grey, good", "Window: uPVC, good, blind good", "Radiator: single panel, TRV",
                  "Wardrobe: double, fitted, good", "Bed: double frame, good", "Mattress: double, protector fitted, good"],
    "Bedroom 2": ["Walls: magnolia, small nail holes x4", "Carpet: grey, slight stain near door (pre-existing)", "Window: uPVC, good",
                  "Radiator: single panel", "Desk: white, good", "Chair: office, good"],
    "Bathroom": ["Walls: fully tiled, grout slightly discoloured", "Floor: vinyl, good", "Bath: acrylic with shower over, mixer, working",
                 "Shower screen: glass, good", "WC: working, seat good", "Basin: working, plug chain present", "Extractor fan: ceiling, working",
                 "Towel radiator: working", "Mirror cabinet: good"],
    "Meter readings & keys": ["Electric meter: 48213.7 (cupboard, hallway)", "Gas meter: 09871.2", "Water: unmetered",
                              "Keys: 2x front door, 2x post box, 1x bike store fob", "Parking: bay 7"],
}


def make_inventory_pages() -> list[list[str]]:
    pages = []
    head = ["RIVERSIDE COURT - CHECK-IN INVENTORY AND SCHEDULE OF CONDITION", "Flat 7, Riverside Court, 3 Wharf Lane, Bristol BS1 6XY",
            "Tenancy start: 1 April 2024    Tenants: Grace Adeyemi, Sam Whitlock", "Prepared by: Clearview Inventories Ltd    Clerk: R. Dawes",
            "Condition key: good / fair / poor. All items landlord-owned unless stated.", ""]
    for i, (room, items) in enumerate(ROOMS.items()):
        lines = (head if i == 0 else [f"Flat 7 Riverside Court - inventory (continued)", ""]) + [f"ROOM: {room.upper()}", ""]
        for j, it in enumerate(items, 1):
            lines.append(f"  {room[:3].upper()}-{j:02d}  {it}")
        lines += ["", f"Photographs: see appendix {i + 1} (not attached to this copy)", ""]
        if room == "Meter readings & keys":
            lines += ["", "DECLARATION", "Tenants confirm the above is an accurate record at check-in.",
                      "Signed: G. Adeyemi   S. Whitlock   Date: 01/04/2024"]
        pages.append(lines)
    return pages


# ----------------------------------------------------------------------------
# 08: repair log CSV (60 rows across the block; a handful are Flat 7)
# ----------------------------------------------------------------------------

def make_repair_log(out: Path) -> None:
    rng = random.Random(8)
    cats = ["plumbing", "electrical", "heating", "appliance", "communal", "decor", "locks", "pest"]
    descs = {
        "plumbing": ["dripping tap", "slow drain", "toilet running", "shower head replaced"],
        "electrical": ["socket not working", "light fitting replaced", "RCD tripping", "extractor fan replaced"],
        "heating": ["radiator cold", "boiler service", "boiler pressure loss", "thermostat replaced"],
        "appliance": ["oven element", "fridge not cooling", "hob ignition", "dishwasher not draining"],
        "communal": ["lift fault reported to block mgmt", "stair light out", "entry phone fault", "bin store door"],
        "decor": ["touch-up after leak", "sealant renewed", "blind replaced", "carpet cleaned"],
        "locks": ["lock change at tenancy end", "post box lock", "window handle", "door closer adjusted"],
        "pest": ["ants in kitchen", "silverfish bathroom", "wasps balcony", "mice communal bin area"],
    }
    flats = [f"Flat {n}" for n in range(1, 13)]
    rows = []
    d = date(2024, 9, 1)
    for i in range(55):
        d += timedelta(days=rng.randint(5, 16))
        c = rng.choice(cats)
        rows.append([f"RC-{1000 + i}", d.isoformat(), rng.choice(flats), c, rng.choice(descs[c]), rng.choice(["ApplianceFix SW", "Wharf Plumbing", "Bright Spark", "HandyPro", "block mgmt"]), rng.choice([0, 60, 75, 85, 95, 110, 140]), "completed"])
    flat7 = [
        ["RC-2001", "2025-11-04", "Flat 7", "appliance", "Washing machine Beko WTK94121W not spinning - carbon brushes replaced", "ApplianceFix SW", 120, "completed"],
        ["RC-2002", "2026-05-21", "Flat 7", "appliance", "Washing machine leaking from door seal - seal replaced", "ApplianceFix SW", 135, "completed"],
        ["RC-2003", "2026-08-30", "Flat 7", "appliance", "Washing machine bearing noise + intermittent leak at pump housing. Temp fix. ENGINEER: beyond economical repair, recommend replacement approx GBP 350 fitted", "ApplianceFix SW", 110, "completed - replacement recommended"],
        ["RC-2004", "2026-09-14", "Flat 6", "decor", "Kitchen ceiling stain investigation - possible ingress from Flat 7 above, monitor", "HandyPro", 0, "monitoring"],
        ["RC-2005", "2026-06-02", "Flat 7", "heating", "Boiler annual service", "Wharf Plumbing", 80, "completed"],
    ]
    rows += flat7
    rows.sort(key=lambda r: r[1])
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["job_ref", "date", "unit", "category", "description", "contractor", "cost_gbp", "status"])
        w.writerows(rows)


# ----------------------------------------------------------------------------
# 08: a small PNG "photo" (a flat-floor pattern with a dark puddle), pure stdlib
# ----------------------------------------------------------------------------

def make_png(out: Path, w: int = 320, h: int = 240) -> None:
    rows = []
    for y in range(h):
        row = bytearray([0])
        for x in range(w):
            tile = ((x // 40) + (y // 40)) % 2
            r, g, b = (198, 190, 176) if tile else (184, 176, 160)
            dx, dy = x - 200, y - 150
            if dx * dx / 2.2 + dy * dy < 60 * 60:
                r, g, b = (96, 92, 84)
            row += bytes((r, g, b))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    out.write_bytes(png)


if __name__ == "__main__":
    c7 = CASES / "07_noisy_group_chat"
    c7.mkdir(parents=True, exist_ok=True)
    (c7 / "whatsapp_group_export.txt").write_text(make_group_chat())

    c8 = CASES / "08_large_context_washing_machine"
    c8.mkdir(parents=True, exist_ok=True)
    make_pdf(make_inventory_pages(), c8 / "inventory_checkin_2024.pdf")
    make_repair_log(c8 / "block_repair_log.csv")
    make_png(c8 / "photo_kitchen_floor.png")
    for p in [c7 / "whatsapp_group_export.txt", c8 / "inventory_checkin_2024.pdf", c8 / "block_repair_log.csv", c8 / "photo_kitchen_floor.png"]:
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:,} bytes")
