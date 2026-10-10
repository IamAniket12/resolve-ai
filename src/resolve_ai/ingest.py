"""Turn whatever the hackathon gives us (folders of files, JSON dumps, emails,
PDFs, call recordings, photos) into one normalised CaseBundle per case.

Discovery rules (first match wins):
  1. `cases_path` is a file ending .json containing a list  -> one case per element
  2. `cases_path` contains sub-directories                    -> one case per sub-directory
  3. `cases_path` contains only files                         -> one case per file
A case directory is read recursively.
"""
from __future__ import annotations

import csv
import email
import io
import json
import logging
from email import policy as email_policy
from pathlib import Path
from typing import Callable, List, Optional

from resolve_ai.models import Attachment, CaseBundle

log = logging.getLogger(__name__)

TEXT_EXT = {".txt", ".md", ".log", ".rst"}
JSON_EXT = {".json", ".jsonl", ".yaml", ".yml"}
CSV_EXT = {".csv", ".tsv"}
EMAIL_EXT = {".eml", ".msg"}
PDF_EXT = {".pdf"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
HTML_EXT = {".html", ".htm"}
SKIP_NAMES = {".DS_Store", "Thumbs.db"}

Transcriber = Optional[Callable[[Path], str]]


def _read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_bytes().decode("utf-8", errors="replace")


def _load_json_text(path: Path) -> str:
    raw = _read_text(path)
    if path.suffix == ".jsonl":
        rows = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    rows.append({"_unparsed": line})
        return json.dumps(rows, indent=2, ensure_ascii=False)
    if path.suffix in {".yaml", ".yml"}:
        return raw  # keep as-is; the model reads YAML fine
    try:
        return json.dumps(json.loads(raw), indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return raw


def _load_csv_text(path: Path) -> str:
    raw = _read_text(path)
    delim = "\t" if path.suffix == ".tsv" else ","
    rows = list(csv.reader(io.StringIO(raw), delimiter=delim))
    if not rows:
        return ""
    header, body = rows[0], rows[1:]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in body[:500]:
        lines.append("| " + " | ".join(c.replace("\n", " ") for c in r) + " |")
    if len(body) > 500:
        lines.append(f"... {len(body) - 500} more rows")
    return "\n".join(lines)


def _load_email_text(path: Path) -> str:
    try:
        msg = email.message_from_bytes(path.read_bytes(), policy=email_policy.default)
    except Exception as e:  # noqa: BLE001
        return _read_text(path)
    headers = [f"{h}: {msg[h]}" for h in ("From", "To", "Cc", "Date", "Subject") if msg[h]]
    body = ""
    try:
        part = msg.get_body(preferencelist=("plain", "html"))
        if part is not None:
            body = part.get_content()
    except Exception:  # noqa: BLE001
        body = msg.get_payload(decode=True) or b""
        body = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body)
    attachments = [p.get_filename() for p in msg.iter_attachments() if p.get_filename()]
    out = "\n".join(headers) + "\n\n" + body
    if attachments:
        out += "\n\n[email attachments: " + ", ".join(attachments) + "]"
    return out


def _load_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return "(pypdf not installed - PDF text unavailable)"
    try:
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages[:60]):
            pages.append(f"--- page {i + 1} ---\n{page.extract_text() or ''}")
        return "\n".join(pages)
    except Exception as e:  # noqa: BLE001
        return f"(could not read PDF: {e})"


def _strip_html(raw: str) -> str:
    import re
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def load_attachment(path: Path, transcriber: Transcriber = None) -> Attachment:
    ext = path.suffix.lower()
    name = path.name
    try:
        if ext in TEXT_EXT:
            kind = "transcript" if "transcript" in name.lower() or "call" in name.lower() else "text"
            return Attachment(name, kind, _read_text(path), str(path))
        if ext in JSON_EXT:
            return Attachment(name, "json", _load_json_text(path), str(path))
        if ext in CSV_EXT:
            return Attachment(name, "csv", _load_csv_text(path), str(path))
        if ext in EMAIL_EXT:
            return Attachment(name, "email", _load_email_text(path), str(path))
        if ext in PDF_EXT:
            return Attachment(name, "pdf", _load_pdf_text(path), str(path))
        if ext in HTML_EXT:
            return Attachment(name, "text", _strip_html(_read_text(path)), str(path))
        if ext in IMAGE_EXT:
            mt = {"jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext[1:], f"image/{ext[1:]}")
            return Attachment(name, "image", "", str(path), media_type=mt)
        if ext in AUDIO_EXT:
            sibling = next((p for p in path.parent.glob(path.stem + ".*") if p.suffix.lower() in TEXT_EXT), None)
            if transcriber is not None:
                try:
                    return Attachment(name, "transcript", transcriber(path), str(path), note="audio transcribed with ElevenLabs Scribe")
                except Exception as e:  # noqa: BLE001
                    log.warning("transcription failed for %s: %s", path, e)
                    if sibling is None:
                        return Attachment(name, "audio", "", str(path), note=f"audio present but transcription failed: {e}")
            if sibling is not None:
                return Attachment(name, "transcript", _read_text(sibling), str(path), note=f"audio; transcript taken from {sibling.name}")
            return Attachment(name, "audio", "", str(path), note="audio present but no transcription available (no ELEVENLABS_API_KEY)")
        # unknown: try as text
        text = _read_text(path)
        if "\x00" in text[:1000]:
            return Attachment(name, "unknown", "", str(path), note="binary file, not read")
        return Attachment(name, "text", text, str(path))
    except Exception as e:  # noqa: BLE001
        log.exception("failed to load %s", path)
        return Attachment(name, "unknown", "", str(path), note=f"could not load: {e}")


def _files_in(dir_path: Path) -> List[Path]:
    files = [p for p in sorted(dir_path.rglob("*")) if p.is_file() and p.name not in SKIP_NAMES and not p.name.startswith(".")]
    return files


def _case_from_dir(dir_path: Path, transcriber: Transcriber) -> CaseBundle:
    atts = [load_attachment(p, transcriber) for p in _files_in(dir_path)]
    # audio with a transcript sibling: drop the duplicate text sibling to avoid double-counting
    seen_transcript_sources = {a.path for a in atts if a.kind == "transcript" and a.note.startswith("audio; transcript taken from")}
    if seen_transcript_sources:
        stems = {Path(p).stem for p in seen_transcript_sources}
        atts = [a for a in atts if not (a.kind in {"text", "transcript"} and Path(a.name).stem in stems and a.path and Path(a.path).suffix.lower() in TEXT_EXT)]
    return CaseBundle(case_id=dir_path.name, source=str(dir_path), attachments=atts)


def _case_from_json_item(item, idx: int, source: str) -> CaseBundle:
    cid = None
    if isinstance(item, dict):
        for key in ("case_id", "id", "case", "ticket_id", "reference"):
            if key in item and item[key] not in (None, ""):
                cid = str(item[key])
                break
    cid = cid or str(idx + 1)
    text = json.dumps(item, indent=2, ensure_ascii=False) if not isinstance(item, str) else item
    return CaseBundle(case_id=cid, source=f"{source}#{idx}", attachments=[Attachment(f"case_{cid}.json", "json", text)])


def discover_cases(cases_path: str | Path, transcriber: Transcriber = None) -> List[CaseBundle]:
    root = Path(cases_path)
    if not root.exists():
        raise FileNotFoundError(f"cases path not found: {root}")
    if root.is_file() and root.suffix.lower() == ".zip":
        import zipfile
        target = root.with_name(root.stem + "_extracted")
        if not target.exists():
            with zipfile.ZipFile(root) as z:
                z.extractall(target)
        # a zip usually wraps everything in one top-level folder
        inner = [p for p in target.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))]
        files_here = [p for p in target.iterdir() if p.is_file()]
        root = inner[0] if len(inner) == 1 and not files_here else target
    if root.is_file():
        if root.suffix.lower() in {".json", ".jsonl"}:
            text = _read_text(root)
            data = [json.loads(l) for l in text.splitlines() if l.strip()] if root.suffix == ".jsonl" else json.loads(text)
            if isinstance(data, dict):
                for key in ("cases", "items", "data", "tickets"):
                    if isinstance(data.get(key), list):
                        data = data[key]
                        break
            if isinstance(data, list):
                return [_case_from_json_item(item, i, str(root)) for i, item in enumerate(data)]
        return [CaseBundle(root.stem, str(root), [load_attachment(root, transcriber)])]

    subdirs = [p for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith((".", "_"))]
    if subdirs:
        def has_files(d: Path) -> bool:
            return any(x.is_file() and not x.name.startswith(".") for x in d.iterdir())
        if not any(has_files(d) for d in subdirs):
            # e.g. <root>/Property Management/001/index.md : the first level is a track/group, descend one level
            bundles: List[CaseBundle] = []
            for group in subdirs:
                inner = [p for p in sorted(group.iterdir()) if p.is_dir() and not p.name.startswith((".", "_"))]
                for d in inner:
                    b = _case_from_dir(d, transcriber)
                    if len(subdirs) > 1:
                        b.case_id = f"{group.name}__{d.name}".replace(" ", "_")
                    bundles.append(b)
            if bundles:
                return bundles
        return [_case_from_dir(d, transcriber) for d in subdirs]
    files = _files_in(root)
    return [CaseBundle(p.stem, str(p), [load_attachment(p, transcriber)]) for p in files]
